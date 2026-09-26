"""PostgreSQL / TimescaleDB repository implementation for monitoring data ingestion.

Handles execution lifecycle management, dimension synchronization,
staging ingestion, and specialized metric fact loading.
"""

# =============================================================
# Imports
# =============================================================
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

import psycopg
from psycopg.rows import dict_row

from collector.core.exceptions import DatabaseConnectionError, StagingLoadError
from collector.core.logging import setup_logger

logger = setup_logger(__name__)

SpecializedKind = Literal["wait", "blocking", "query", "backup", "agent", "deadlock"]


# =============================================================
# Repository Implementation
# =============================================================
class PostgresRepository:
    """Encapsulates data persistence operations against PostgreSQL/TimescaleDB."""

    def __init__(self, dsn: str) -> None:
        """Initialize repository with PostgreSQL DSN.

        Args:
            dsn: PostgreSQL connection string.
        """
        self._dsn = dsn

    # =============================================================
    # Connection Management
    # =============================================================
    def _get_connection(self) -> psycopg.Connection:
        """Establish and return a new database connection."""
        try:
            return psycopg.connect(self._dsn, row_factory=dict_row)
        except Exception as exc:
            logger.error("Failed to connect to PostgreSQL repository: %s", exc)
            raise DatabaseConnectionError(f"PostgreSQL connection error: {exc}") from exc

    # =============================================================
    # Collection Run Lifecycle
    # =============================================================
    def create_collection_run(
        self,
        instance_key: int,
        collector_name: str,
        collector_version: str,
    ) -> int:
        """Register the initiation of a collection cycle.

        Args:
            instance_key: Target SQL Server instance surrogate key.
            collector_name: Name of the executing collector.
            collector_version: Semantic version of the collector.

        Returns:
            int: Assigned collection run key.
        """
        query = """
            INSERT INTO monitoring.collection_run (
                instance_key,
                started_at,
                status,
                collector_name,
                collector_version
            ) VALUES (%s, %s, 'running', %s, %s)
            RETURNING collection_run_key;
        """
        now_utc = datetime.now(timezone.utc)

        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(query, (instance_key, now_utc, collector_name, collector_version))
            result = cur.fetchone()
            conn.commit()
            return int(result["collection_run_key"])

    def finalize_collection_run(
        self,
        run_key: int,
        requested_metrics: int,
        collected_metrics: int,
        records_collected: int,
    ) -> str:
        """Finalize metrics collection status, calculate duration and record metrics summary.

        Args:
            run_key: Collection run identifier.
            requested_metrics: Number of target metrics planned.
            collected_metrics: Number of successfully extracted metrics.
            records_collected: Total record count ingested.

        Returns:
            str: Resolved execution status ('success', 'partial', or 'failed').
        """
        finished_at = datetime.now(timezone.utc)

        with self._get_connection() as conn, conn.cursor() as cur:
            cur.execute(
                """
                SELECT error_count, started_at
                FROM monitoring.collection_run
                WHERE collection_run_key = %s;
                """,
                (run_key,),
            )
            run_record = cur.fetchone()

            if not run_record:
                raise StagingLoadError(f"Collection run key {run_key} not found.")

            error_count = run_record["error_count"]
            started_at = run_record["started_at"]
            duration_sec = (finished_at - started_at).total_seconds()

            if error_count == 0 and collected_metrics == requested_metrics:
                status = "success"
            elif collected_metrics > 0:
                status = "partial"
            else:
                status = "failed"

            cur.execute(
                """
                UPDATE monitoring.collection_run
                SET finished_at = %s,
                    status = %s,
                    duration_seconds = %s,
                    metrics_requested = %s,
                    metrics_collected = %s,
                    records_collected = %s
                WHERE collection_run_key = %s;
                """,
                (
                    finished_at,
                    status,
                    duration_sec,
                    requested_metrics,
                    collected_metrics,
                    records_collected,
                    run_key,
                ),
            )
            conn.commit()
            return status

    def log_collection_error(
        self,
        run_key: int,
        instance_key: int,
        error_type: str,
        error_message: str,
        metric_code: Optional[str] = None,
    ) -> None:
        """Record non-fatal collection errors and increment the run error counter."""
        query = """
            INSERT INTO monitoring.collection_error (
                collection_run_key,
                instance_key,
                metric_key,
                error_type,
                error_message
            )
            SELECT
                %s,
                %s,
                m.metric_key,
                %s,
                %s
            FROM (SELECT 1) dummy
            LEFT JOIN dimension.dim_metric m ON m.metric_code = %s;
        """
        try:
            with self._get_connection() as conn, conn.cursor() as cur:
                cur.execute(
                    query,
                    (run_key, instance_key, error_type, str(error_message), metric_code),
                )
                cur.execute(
                    """
                    UPDATE monitoring.collection_run
                    SET error_count = error_count + 1
                    WHERE collection_run_key = %s;
                    """,
                    (run_key,),
                )
                conn.commit()
        except Exception as exc:
            logger.error("Failed to persist collection error log: %s", exc)

    # =============================================================
    # Dimension Synchronization
    # =============================================================
    def sync_databases(self, rows: List[Dict[str, Any]]) -> None:
        """Upsert target instance databases into dimension.dim_database."""
        if not rows:
            return

        query = """
            INSERT INTO dimension.dim_database (
                instance_key,
                database_name,
                database_id,
                recovery_model,
                compatibility_level,
                is_system_database,
                is_active
            ) VALUES (
                %(instance_key)s,
                %(database_name)s,
                %(database_id)s,
                %(recovery_model)s,
                %(compatibility_level)s,
                %(is_system_database)s,
                TRUE
            )
            ON CONFLICT (instance_key, database_name) DO UPDATE SET
                database_id = EXCLUDED.database_id,
                recovery_model = EXCLUDED.recovery_model,
                compatibility_level = EXCLUDED.compatibility_level,
                is_system_database = EXCLUDED.is_system_database,
                is_active = TRUE,
                updated_at = CURRENT_TIMESTAMP;
        """
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.executemany(query, rows)
            conn.commit()

    # =============================================================
    # Staging Ingestion
    # =============================================================
    def insert_staging_server_metrics(self, rows: List[Dict[str, Any]]) -> int:
        """Batch insert raw host/server level metrics into staging."""
        if not rows:
            return 0

        query = """
            INSERT INTO staging.server_metric (
                collection_run_key,
                instance_key,
                metric_code,
                collected_at,
                metric_value_numeric,
                metric_value_text,
                status,
                source_record_id
            ) VALUES (
                %(collection_run_key)s,
                %(instance_key)s,
                %(metric_code)s,
                %(collected_at)s,
                %(metric_value_numeric)s,
                %(metric_value_text)s,
                %(status)s,
                %(source_record_id)s
            );
        """
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.executemany(query, rows)
            conn.commit()
            return len(rows)

    def insert_staging_database_metrics(self, rows: List[Dict[str, Any]]) -> int:
        """Batch insert raw database-level metrics mapped to dimension keys."""
        if not rows:
            return 0

        query = """
            INSERT INTO staging.database_metric (
                collection_run_key,
                database_key,
                metric_code,
                collected_at,
                metric_value_numeric,
                metric_value_text,
                status,
                source_record_id
            )
            SELECT
                %(collection_run_key)s,
                d.database_key,
                %(metric_code)s,
                %(collected_at)s,
                %(metric_value_numeric)s,
                %(metric_value_text)s,
                %(status)s,
                %(source_record_id)s
            FROM dimension.dim_database d
            WHERE d.instance_key = %(instance_key)s
              AND d.database_name = %(database_name)s
              AND d.is_active = TRUE;
        """
        with self._get_connection() as conn, conn.cursor() as cur:
            cur.executemany(query, rows)
            conn.commit()
            return len(rows)

    # =============================================================
    # Specialized Facts Ingestion
    # =============================================================
    def insert_specialized(self, kind: SpecializedKind, rows: List[Dict[str, Any]]) -> int:
        """Ingest domain-specialized metrics into their respective fact tables."""
        if not rows:
            return 0

        with self._get_connection() as conn, conn.cursor() as cur:
            if kind == "wait":
                query = """
                    INSERT INTO fact.fact_wait_stat (
                        instance_key,
                        date_key,
                        collected_at,
                        wait_type,
                        waiting_tasks_count,
                        wait_time_ms,
                        signal_wait_time_ms,
                        max_wait_time_ms,
                        resource_wait_time_ms,
                        status,
                        collection_run_key
                    ) VALUES (
                        %s,
                        TO_CHAR(%s AT TIME ZONE 'UTC', 'YYYYMMDD')::int,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """
                params = [
                    (
                        r["instance_key"],
                        r["collected_at"],
                        r["collected_at"],
                        r["wait_type"],
                        r["waiting_tasks_count"],
                        r["wait_time_ms"],
                        r["signal_wait_time_ms"],
                        r["max_wait_time_ms"],
                        r["resource_wait_time_ms"],
                        r["status"],
                        r["collection_run_key"],
                    )
                    for r in rows
                ]

            elif kind == "blocking":
                query = """
                    INSERT INTO fact.fact_blocking (
                        instance_key,
                        database_key,
                        date_key,
                        collected_at,
                        blocking_session_id,
                        blocked_session_id,
                        blocking_status,
                        wait_type,
                        wait_time_ms,
                        blocked_login_name,
                        blocked_host_name,
                        blocked_program_name,
                        status,
                        collection_run_key
                    )
                    SELECT
                        %s,
                        d.database_key,
                        TO_CHAR(%s AT TIME ZONE 'UTC', 'YYYYMMDD')::int,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    FROM dimension.dim_database d
                    WHERE d.instance_key = %s
                      AND d.database_name = %s;
                """
                params = [
                    (
                        r["instance_key"],
                        r["collected_at"],
                        r["collected_at"],
                        r["blocking_session_id"],
                        r["blocked_session_id"],
                        r.get("blocking_status"),
                        r.get("wait_type"),
                        r.get("wait_time_ms"),
                        r.get("blocked_login_name"),
                        r.get("blocked_host_name"),
                        r.get("blocked_program_name"),
                        r["status"],
                        r["collection_run_key"],
                        r["instance_key"],
                        r.get("database_name"),
                    )
                    for r in rows
                    if r.get("database_name")
                ]

            elif kind == "query":
                query = """
                    INSERT INTO fact.fact_query_stat (
                        database_key,
                        instance_key,
                        date_key,
                        collected_at,
                        query_hash,
                        query_plan_hash,
                        sql_handle,
                        plan_handle,
                        query_text,
                        execution_count,
                        total_elapsed_ms,
                        total_cpu_ms,
                        total_logical_reads,
                        total_logical_writes,
                        total_physical_reads,
                        last_elapsed_ms,
                        last_cpu_ms,
                        last_logical_reads,
                        last_logical_writes,
                        min_elapsed_ms,
                        max_elapsed_ms,
                        avg_elapsed_ms,
                        avg_cpu_ms,
                        avg_logical_reads,
                        status,
                        collection_run_key
                    )
                    SELECT
                        d.database_key,
                        %s,
                        TO_CHAR(%s AT TIME ZONE 'UTC', 'YYYYMMDD')::int,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    FROM dimension.dim_database d
                    WHERE d.instance_key = %s
                      AND d.database_name = %s;
                """
                params = [
                    (
                        r["instance_key"],
                        r["collected_at"],
                        r["collected_at"],
                        r.get("query_hash"),
                        r.get("query_plan_hash"),
                        r.get("sql_handle"),
                        r.get("plan_handle"),
                        r.get("query_text"),
                        r.get("execution_count"),
                        r.get("total_elapsed_ms"),
                        r.get("total_cpu_ms"),
                        r.get("total_logical_reads"),
                        r.get("total_logical_writes"),
                        r.get("total_physical_reads"),
                        r.get("last_elapsed_ms"),
                        r.get("last_cpu_ms"),
                        r.get("last_logical_reads"),
                        r.get("last_logical_writes"),
                        r.get("min_elapsed_ms"),
                        r.get("max_elapsed_ms"),
                        r.get("avg_elapsed_ms"),
                        r.get("avg_cpu_ms"),
                        r.get("avg_logical_reads"),
                        r["status"],
                        r["collection_run_key"],
                        r["instance_key"],
                        r.get("database_name"),
                    )
                    for r in rows
                    if r.get("database_name")
                ]

            elif kind == "backup":
                query = """
                    INSERT INTO fact.fact_backup (
                        instance_key,
                        database_key,
                        date_key,
                        backup_start_at,
                        backup_finish_at,
                        backup_type,
                        backup_status,
                        duration_seconds,
                        backup_size_bytes,
                        compressed_backup_size_bytes,
                        physical_device_type,
                        backup_set_id,
                        status,
                        collection_run_key
                    )
                    SELECT
                        %s,
                        d.database_key,
                        TO_CHAR(%s AT TIME ZONE 'UTC', 'YYYYMMDD')::int,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    FROM dimension.dim_database d
                    WHERE d.instance_key = %s
                      AND d.database_name = %s;
                """
                params = [
                    (
                        r["instance_key"],
                        r["backup_start_at"],
                        r["backup_start_at"],
                        r.get("backup_finish_at"),
                        r.get("backup_type"),
                        r.get("backup_status"),
                        r.get("duration_seconds"),
                        r.get("backup_size_bytes"),
                        r.get("compressed_backup_size_bytes"),
                        r.get("physical_device_type"),
                        r.get("backup_set_id"),
                        r["status"],
                        r["collection_run_key"],
                        r["instance_key"],
                        r.get("database_name"),
                    )
                    for r in rows
                    if r.get("database_name")
                ]

            elif kind == "agent":
                query = """
                    INSERT INTO fact.fact_sqlagent_job (
                        instance_key,
                        date_key,
                        collected_at,
                        job_id,
                        job_name,
                        run_id,
                        run_start_at,
                        run_finish_at,
                        duration_seconds,
                        run_status,
                        message,
                        sqlagent_job_enabled,
                        status,
                        collection_run_key
                    ) VALUES (
                        %s,
                        TO_CHAR(%s AT TIME ZONE 'UTC', 'YYYYMMDD')::int,
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    );
                """
                params = [
                    (
                        r["instance_key"],
                        r["collected_at"],
                        r["collected_at"],
                        r.get("job_id"),
                        r["job_name"],
                        r.get("run_id"),
                        r.get("run_start_at"),
                        r.get("run_finish_at"),
                        r.get("run_duration_seconds"),
                        r["run_status"],
                        r.get("message"),
                        r.get("sqlagent_job_enabled"),
                        r["status"],
                        r["collection_run_key"],
                    )
                    for r in rows
                ]

            elif kind == "deadlock":
                query = """
                    INSERT INTO fact.fact_deadlock (
                        instance_key,
                        date_key,
                        occurred_at,
                        deadlock_type,
                        deadlock_graph,
                        deadlock_hash,
                        status,
                        collection_run_key
                    ) VALUES (
                        %s,
                        TO_CHAR(%s AT TIME ZONE 'UTC', 'YYYYMMDD')::int,
                        %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (instance_key, deadlock_hash) DO NOTHING;
                """
                params = [
                    (
                        r["instance_key"],
                        r["occurred_at"],
                        r["occurred_at"],
                        r.get("deadlock_type"),
                        r.get("deadlock_graph"),
                        r.get("deadlock_hash"),
                        r["status"],
                        r["collection_run_key"],
                    )
                    for r in rows
                ]
            else:
                logger.warning("Unrecognized specialized metric kind: %s", kind)
                return 0

            if params:
                cur.executemany(query, params)
                conn.commit()
                return len(params)
            return 0

    # =============================================================
    # Staging ETL Trigger Procedures
    # =============================================================
    def execute_staging_load_procedures(self, run_key: int) -> None:
        """Trigger stored procedures to transform staging data into fact tables."""
        with self._get_connection() as conn, conn.cursor() as cur:
            try:
                cur.execute("CALL monitoring.sp_load_server_metrics(%s);", (run_key,))
                cur.execute("CALL monitoring.sp_load_database_metrics(%s);", (run_key,))
                conn.commit()
            except Exception as exc:
                conn.rollback()
                logger.error("Failed to execute staging load procedures: %s", exc)
                raise StagingLoadError(
                    f"Staging ELT procedure execution failed: {exc}"
                ) from exc