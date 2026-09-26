"""SQL Server Instance Health and Heartbeat Monitoring DAG.

Continuously verifies connectivity across all registered SQL Server instances
and updates the monitoring.system_health operational table.
"""

from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pymssql

from collector.core.config import get_settings

logger = logging.getLogger("airflow.task")

ACTIVE_TARGETS_QUERY = """
SELECT 
    i.instance_key,
    s.host_name,
    i.port,
    COALESCE(t.connection_timeout_seconds, 10) AS connection_timeout
FROM config.monitoring_target t
JOIN dimension.dim_instance i ON i.instance_key = t.instance_key
JOIN dimension.dim_server s ON s.server_key = i.server_key
WHERE t.enabled AND i.is_active AND s.is_active
ORDER BY t.instance_key;
"""

UPSERT_HEALTH_QUERY = """
INSERT INTO monitoring.system_health (
    component_name,
    component_type,
    status,
    host_name,
    last_heartbeat_at,
    last_success_at,
    last_error_at,
    message,
    consecutive_failures,
    updated_at
) VALUES (
    %(component_name)s,
    'sqlserver_instance',
    %(status)s,
    %(host_name)s,
    NOW(),
    CASE WHEN %(status)s = 'healthy' THEN NOW() ELSE NULL END,
    CASE WHEN %(status)s = 'unhealthy' THEN NOW() ELSE NULL END,
    %(message)s,
    CASE WHEN %(status)s = 'healthy' THEN 0 ELSE 1 END,
    NOW()
)
ON CONFLICT (component_name) DO UPDATE SET
    status = EXCLUDED.status,
    host_name = EXCLUDED.host_name,
    last_heartbeat_at = NOW(),
    last_success_at = CASE 
        WHEN EXCLUDED.status = 'healthy' THEN NOW() 
        ELSE monitoring.system_health.last_success_at 
    END,
    last_error_at = CASE 
        WHEN EXCLUDED.status = 'unhealthy' THEN NOW() 
        ELSE monitoring.system_health.last_error_at 
    END,
    message = EXCLUDED.message,
    consecutive_failures = CASE 
        WHEN EXCLUDED.status = 'healthy' THEN 0 
        ELSE monitoring.system_health.consecutive_failures + 1 
    END,
    updated_at = NOW();
"""


@dag(
    dag_id="sqlserver_monitoring",
    schedule="*/2 * * * *",  # Health check every 2 minutes
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data_platform",
        "retries": 1,
        "retry_delay": timedelta(seconds=20),
    },
    tags=["sqlserver", "health", "heartbeat"],
)
def sqlserver_monitoring_dag():

    @task
    def fetch_active_instances() -> List[Dict[str, Any]]:
        """Fetch list of all active instances for heartbeat probe."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        rows = hook.get_records(ACTIVE_TARGETS_QUERY)

        targets = [
            {
                "instance_key": row[0],
                "host_name": row[1],
                "port": row[2] or 1433,
                "timeout": row[3],
            }
            for row in rows
        ]
        logger.info("Found %d active SQL Server instances for health checking.", len(targets))
        return targets

    @task
    def probe_instance_health(target: Dict[str, Any]) -> Dict[str, Any]:
        """Perform ping query against target SQL Server and update system_health."""
        instance_key = target["instance_key"]
        host_name = target["host_name"]
        port = target["port"]
        timeout = target["timeout"]

        base_settings = get_settings()
        # Keys must match the Settings model's actual field names
        # (SCREAMING_SNAKE_CASE) -- see the matching note in
        # sqlserver_collection.py for why this matters.
        settings = base_settings.model_copy(
            update={
                "TARGET_INSTANCE_KEY": instance_key,
                "SQLSERVER_HOST": host_name,
                "SQLSERVER_PORT": port,
                "SQLSERVER_CONNECTION_TIMEOUT": timeout,
            }
        )

        status = "healthy"
        message = "SQL Server connection succeeded"

        try:
            # Lightweight probe with timeout
            conn = pymssql.connect(
                server=settings.SQLSERVER_HOST,
                port=settings.SQLSERVER_PORT,
                user=settings.SQLSERVER_USER,
                password=settings.SQLSERVER_PASSWORD.get_secret_value(),
                database="master",
                timeout=timeout,
                login_timeout=timeout,
                as_dict=True,
            )
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1 AS health_check;")
                    cursor.fetchone()
            logger.info("Health probe PASSED for instance_key=%s (%s:%s)", instance_key, host_name, port)
        except Exception as exc:
            status = "unhealthy"
            message = f"Connection error: {str(exc)[:250]}"
            logger.warning("Health probe FAILED for instance_key=%s: %s", instance_key, message)

        # Upsert state in monitoring database
        hook = PostgresHook(postgres_conn_id="postgres_default")
        conn_pg = hook.get_conn()
        with conn_pg.cursor() as cursor:
            cursor.execute(
                UPSERT_HEALTH_QUERY,
                {
                    "component_name": f"sqlserver:{instance_key}",
                    "status": status,
                    "host_name": host_name,
                    "message": message,
                },
            )
            conn_pg.commit()

        return {
            "instance_key": instance_key,
            "status": status,
            "message": message,
        }

    # Parallel mapped health probes
    targets = fetch_active_instances()
    probe_instance_health.expand(target=targets)


sqlserver_monitoring = sqlserver_monitoring_dag()