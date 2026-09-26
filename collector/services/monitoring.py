"""Monitoring orchestration service.

Coordinates SQL Server DMV extraction pipelines, derived metric computations,
PostgreSQL staging ingestion, and ELT transformations.
"""

# =============================================================
# Imports
# =============================================================
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Tuple

from collector.core.config import Settings
from collector.core.logging import setup_logger
from collector.repository.postgres import PostgresRepository
from collector.sqlserver.backups import collect_backup_metrics
from collector.sqlserver.blocking import collect_blocking_metrics
from collector.sqlserver.connection import get_sql_connection
from collector.sqlserver.database_metrics import collect_database_metrics,sync_databases
from collector.sqlserver.deadlocks import collect_deadlocks
from collector.sqlserver.query_metrics import collect_query_metrics
from collector.sqlserver.server_metrics import collect_server_metrics
from collector.sqlserver.sql_agent import collect_agent_metrics
from collector.sqlserver.wait_stats import collect_wait_stats

# =============================================================
# Logger Setup
# =============================================================
logger = setup_logger(__name__)

# -------------------------------------------------------------------------
# Collector Registry
# -------------------------------------------------------------------------

COLLECTORS: Tuple[Tuple[str, Callable, str], ...] = (
    ("server_metrics", collect_server_metrics, "server"),
    ("wait_stats", collect_wait_stats, "wait"),
    ("blocking", collect_blocking_metrics, "blocking"),
    ("deadlocks", collect_deadlocks, "deadlock"),
    ("query_stats", collect_query_metrics, "query"),
    ("sql_agent", collect_agent_metrics, "agent"),
    ("database_metrics", collect_database_metrics, "database"),
    ("backups", collect_backup_metrics, "backup"),
)

# =============================================================
# Monitoring Service Implementation
# =============================================================
class MonitoringService:
    """Coordinates metric collection, staging ingestion, and ELT execution."""

    def __init__(
        self,
        settings: Settings,
        repo: PostgresRepository,
    ) -> None:
        self.settings = settings
        self.repo = repo

    # ---------------------------------------------------------------------
    # Derived Metric Calculations
    # ---------------------------------------------------------------------

    @staticmethod
    def _derive_blocking_summary(
        run_key: int,
        instance_key: int,
        rows: List[Dict[str, Any]],
        now_utc: datetime,
    ) -> List[Dict[str, Any]]:
        """Build summary metric for the number of currently blocked sessions."""

        return [
            {
                "collection_run_key": run_key,
                "instance_key": instance_key,
                "metric_code": "BLOCKING_SESSION_COUNT",
                "collected_at": now_utc,
                "metric_value_numeric": float(len(rows)),
                "metric_value_text": None,
                "status": "success",
                "source_record_id": None,
            }
        ]
    # =============================================================
    # Derived Metric Transformers
    # =============================================================
    @staticmethod
    def _derive_agent_failures_summary(
        run_key: int,
        instance_key: int,
        rows: List[Dict[str, Any]],
        now_utc: datetime,
    ) -> List[Dict[str, Any]]:
        """Build summary metric for failed SQL Server Agent jobs."""

        failed_count = sum(
            1
            for row in rows
            if row.get("run_status") == "FAILED"
        )

        return [
            {
                "collection_run_key": run_key,
                "instance_key": instance_key,
                "metric_code": "SQL_AGENT_FAILURES",
                "collected_at": now_utc,
                "metric_value_numeric": float(failed_count),
                "metric_value_text": None,
                "status": "success",
                "source_record_id": None,
            }
        ]

    @staticmethod
    def _derive_backup_age_metrics(
        rows: List[Dict[str, Any]],
        now_utc: datetime,
    ) -> List[Dict[str, Any]]:
        """Build database-level metrics representing backup age in hours."""

        summaries: List[Dict[str, Any]] = []

        for row in rows:
            finish_time = row.get("backup_finish_at")

            if not finish_time:
                continue

            if finish_time.tzinfo is None:
                finish_time = finish_time.replace(tzinfo=timezone.utc)

            age_hours = max(
                0.0,
                (now_utc - finish_time).total_seconds() / 3600.0,
            )

            summaries.append(
                {
                    "collection_run_key": row["collection_run_key"],
                    "instance_key": row["instance_key"],
                    "database_name": row["database_name"],
                    "metric_code": "BACKUP_AGE_HOURS",
                    "collected_at": now_utc,
                    "metric_value_numeric": age_hours,
                    "metric_value_text": None,
                    "status": "success",
                    "source_record_id": None,
                }
            )

        return summaries

    # ---------------------------------------------------------------------
    # Collection Pipeline
    # ---------------------------------------------------------------------

    def execute_pipeline(self) -> str:
        """Execute the complete SQL Server monitoring collection pipeline."""

        instance_key = self.settings.TARGET_INSTANCE_KEY

        run_key = self.repo.create_collection_run(
            instance_key=instance_key,
            collector_name=self.settings.COLLECTOR_NAME,
            collector_version=self.settings.COLLECTOR_VERSION,
        )

        requested_count = len(COLLECTORS)
        collected_count = 0
        total_records = 0

        logger.info(
            "Initiating collection pipeline run #%s for instance %s",
            run_key,
            instance_key,
        )

        try:
            with get_sql_connection(self.settings) as conn:

                # ---------------------------------------------------------
                # Database Dimension Synchronization
                # ---------------------------------------------------------

                try:
                    db_metadata = sync_databases(
                        conn,
                        run_key,
                        instance_key,
                    )

                    self.repo.sync_databases(db_metadata)

                except Exception:
                    logger.exception(
                        "Database dimension sync failed for run #%s",
                        run_key,
                    )

                    self.repo.log_collection_error(
                        run_key=run_key,
                        instance_key=instance_key,
                        error_type="DatabaseSyncError",
                        error_message="Database dimension synchronization failed.",
                    )

                # ---------------------------------------------------------
                # Metric Collectors
                # ---------------------------------------------------------

                for name, collector_func, metric_type in COLLECTORS:

                    try:
                        logger.debug(
                            "Executing collector: %s",
                            name,
                        )

                        rows = collector_func(
                            conn,
                            run_key,
                            instance_key,
                        )

                        ingested_count = 0
                        now_utc = datetime.now(timezone.utc)

                        # -------------------------------------------------
                        # Standard Server-Level Metrics
                        # -------------------------------------------------

                        if metric_type == "server":
                            ingested_count = (
                                self.repo.insert_staging_server_metrics(rows)
                            )

                        # -------------------------------------------------
                        # Database-Level Metrics
                        # -------------------------------------------------

                        elif metric_type == "database":
                            ingested_count = (
                                self.repo.insert_staging_database_metrics(rows)
                            )

                        # -------------------------------------------------
                        # Specialized Metrics
                        # -------------------------------------------------

                        else:
                            ingested_count = self.repo.insert_specialized(
                                metric_type,
                                rows,
                            )

                            # ---------------------------------------------
                            # Blocking Summary
                            # ---------------------------------------------

                            if metric_type == "blocking":
                                summary = self._derive_blocking_summary(
                                    run_key,
                                    instance_key,
                                    rows,
                                    now_utc,
                                )

                                ingested_count += (
                                    self.repo.insert_staging_server_metrics(
                                        summary
                                    )
                                )

                            # ---------------------------------------------
                            # SQL Agent Failure Summary
                            # ---------------------------------------------

                            elif metric_type == "agent":
                                summary = self._derive_agent_failures_summary(
                                    run_key,
                                    instance_key,
                                    rows,
                                    now_utc,
                                )

                                ingested_count += (
                                    self.repo.insert_staging_server_metrics(
                                        summary
                                    )
                                )

                            # ---------------------------------------------
                            # Backup Age Summary
                            # ---------------------------------------------

                            elif metric_type == "backup":
                                backup_summaries = (
                                    self._derive_backup_age_metrics(
                                        rows,
                                        now_utc,
                                    )
                                )

                                if backup_summaries:
                                    ingested_count += (
                                        self.repo.insert_staging_database_metrics(
                                            backup_summaries
                                        )
                                    )

                        total_records += ingested_count
                        collected_count += 1

                        logger.debug(
                            "Collector '%s' completed successfully "
                            "(records=%s)",
                            name,
                            ingested_count,
                        )

                    except Exception as exc:
                        logger.exception(
                            "Metric collector '%s' failed",
                            name,
                        )

                        self.repo.log_collection_error(
                            run_key=run_key,
                            instance_key=instance_key,
                            error_type="CollectorError",
                            error_message=f"{name}: {exc}",
                        )

            # -------------------------------------------------------------
            # Staging → Fact Transformation
            # -------------------------------------------------------------

            self.repo.execute_staging_load_procedures(run_key)

        except Exception as exc:
            logger.exception(
                "Fatal failure during collection run #%s",
                run_key,
            )

            self.repo.log_collection_error(
                run_key=run_key,
                instance_key=instance_key,
                error_type="FatalRunError",
                error_message=str(exc),
            )

        # -----------------------------------------------------------------
        # Collection Run Finalization
        # -----------------------------------------------------------------

        final_status = self.repo.finalize_collection_run(
            run_key=run_key,
            requested_metrics=requested_count,
            collected_metrics=collected_count,
            records_collected=total_records,
        )

        logger.info(
            "Finalized collection run #%s with status '%s' "
            "(Records: %s, Collectors: %s/%s)",
            run_key,
            final_status,
            total_records,
            collected_count,
            requested_count,
        )

        return final_status