"""Data Quality and Maintenance DAG."""

from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger("airflow.task")

# Retention configuration (in days)
STAGING_RETENTION_DAYS = 3

STAGING_TABLES: List[str] = [
    "staging.server_metric",
    "staging.database_metric",
]

INTEGRITY_CHECKS: List[Dict[str, str]] = [
    {
        "name": "Orphan Server Metrics",
        "query": """
            SELECT COUNT(*)
            FROM fact.fact_server_metric f
            LEFT JOIN dimension.dim_instance i ON i.instance_key = f.instance_key
            WHERE i.instance_key IS NULL;
        """,
    },
    {
        "name": "Orphan Database Metrics",
        "query": """
            SELECT COUNT(*)
            FROM fact.fact_database_metric f
            LEFT JOIN dimension.dim_database d ON d.database_key = f.database_key
            LEFT JOIN dimension.dim_instance i ON i.instance_key = d.instance_key
            WHERE d.database_key IS NULL OR i.instance_key IS NULL;
        """,
    },
    {
        "name": "Orphan Query Metrics",
        "query": """
            SELECT COUNT(*)
            FROM fact.fact_query_stat f
            LEFT JOIN dimension.dim_instance i ON i.instance_key = f.instance_key
            WHERE i.instance_key IS NULL;
        """,
    },
    {
        "name": "Orphan Deadlock Events",
        "query": """
            SELECT COUNT(*)
            FROM fact.fact_deadlock f
            LEFT JOIN dimension.dim_instance i ON i.instance_key = f.instance_key
            WHERE i.instance_key IS NULL;
        """,
    },
]


@dag(
    dag_id="data_quality",
    schedule="0 2 * * *",  # Runs daily at 02:00 AM UTC
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data_platform",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["data-quality", "maintenance", "sqlserver"],
)
def data_quality_dag():

    @task
    def cleanup_staging_tables() -> Dict[str, int]:
        """Purge records older than retention threshold from all staging tables."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        conn = hook.get_conn()
        deleted_summary: Dict[str, int] = {}

        with conn.cursor() as cursor:
            for table in STAGING_TABLES:
                query = f"""
                    DELETE FROM {table}
                    WHERE loaded_at < NOW() - INTERVAL '{STAGING_RETENTION_DAYS} days';
                """
                cursor.execute(query)
                deleted_rows = cursor.rowcount
                deleted_summary[table] = deleted_rows
                logger.info(
                    "Table %s: purged %d rows older than %d days.",
                    table,
                    deleted_rows,
                    STAGING_RETENTION_DAYS,
                )
            conn.commit()

        return deleted_summary

    @task
    def check_referential_integrity() -> None:
        """Validate foreign key relationships and raise exception if orphan rows exist."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        failures: List[Tuple[str, int]] = []

        for check in INTEGRITY_CHECKS:
            check_name = check["name"]
            query = check["query"]

            result = hook.get_first(query)
            orphan_count = result[0] if result else 0

            if orphan_count > 0:
                logger.error("Data Quality check failed: %s found %d orphan records.", check_name, orphan_count)
                failures.append((check_name, orphan_count))
            else:
                logger.info("Check passed: %s (0 orphan records).", check_name)

        if failures:
            error_details = ", ".join([f"{name}: {cnt}" for name, cnt in failures])
            raise ValueError(f"Referential integrity failure detected: {error_details}")

    @task
    def check_future_dated_records() -> None:
        """Sanity check: ensure fact records do not contain future-dated timestamps."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        query = """
            SELECT COUNT(*)
            FROM fact.fact_server_metric
            WHERE collected_at > NOW() + INTERVAL '5 minutes';
        """
        result = hook.get_first(query)
        future_rows = result[0] if result else 0

        if future_rows > 0:
            raise ValueError(f"Found {future_rows} future-dated records in fact_server_metric.")
        logger.info("Timestamp sanity check passed: No future-dated telemetry found.")

    # Execution Flow
    purge_task = cleanup_staging_tables()
    integrity_task = check_referential_integrity()
    future_date_task = check_future_dated_records()

    purge_task >> [integrity_task, future_date_task]


data_quality = data_quality_dag()