from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from croniter import croniter

from collector.core.config import get_settings
from collector.repository.postgres import PostgresRepository
from collector.services.monitoring import MonitoringService


@dag(
    dag_id="sqlserver_collection",
    schedule="* * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "data_platform", "retries": 1, "retry_delay": timedelta(seconds=30)},
    tags=["sqlserver", "collection", "etl"],
)
def sqlserver_collection():
    @task
    def fetch_due_targets() -> list[dict]:
        hook = PostgresHook(postgres_conn_id="postgres_default")
        rows = hook.get_records(
            """
            SELECT
                t.monitoring_target_key,
                t.instance_key,
                s.host_name,
                i.port,
                t.connection_timeout_seconds,
                t.command_timeout_seconds,
                cs.schedule_type,
                cs.interval_seconds,
                cs.cron_expression,
                cs.timezone,
                lr.last_finished
            FROM config.monitoring_target t
            JOIN dimension.dim_instance i ON i.instance_key=t.instance_key
            JOIN dimension.dim_server s ON s.server_key=i.server_key
            LEFT JOIN LATERAL (
                SELECT *
                FROM config.collection_schedule cs
                WHERE cs.monitoring_target_key=t.monitoring_target_key
                  AND cs.enabled
                  AND (cs.start_at IS NULL OR cs.start_at<=NOW())
                  AND (cs.end_at IS NULL OR cs.end_at>NOW())
                ORDER BY cs.priority,cs.collection_schedule_key
                LIMIT 1
            ) cs ON TRUE
            LEFT JOIN LATERAL (
                SELECT MAX(finished_at) AS last_finished
                FROM monitoring.collection_run cr
                WHERE cr.instance_key=t.instance_key
            ) lr ON TRUE
            WHERE t.enabled AND i.is_active AND s.is_active
            ORDER BY t.priority,t.monitoring_target_key
            """
        )
        now = datetime.now(timezone.utc)
        due = []
        for row in rows:
            target_id, instance_key, host_name, port, connection_timeout, command_timeout, schedule_type, interval_seconds, cron_expression, tz_name, last_finished = row
            if last_finished is not None and last_finished.tzinfo is None:
                last_finished = last_finished.replace(tzinfo=timezone.utc)
            if last_finished is None:
                is_due = True
            elif schedule_type == "interval":
                is_due = now >= last_finished + timedelta(seconds=int(interval_seconds))
            elif schedule_type == "cron" and cron_expression:
                try:
                    zone = ZoneInfo(tz_name or "UTC")
                    local_now = now.astimezone(zone)
                    local_last = last_finished.astimezone(zone)
                    is_due = croniter(cron_expression, local_last).get_next(datetime) <= local_now
                except Exception:
                    is_due = False
            else:
                is_due = False
            if is_due:
                due.append({
                    "instance_key": instance_key,
                    "host_name": host_name,
                    "port": port or 1433,
                    "connection_timeout_seconds": connection_timeout,
                    "command_timeout_seconds": command_timeout,
                })
        return due

    @task
    def collect(target: dict) -> str:
        base = get_settings()
        settings = base.model_copy(
            update={
                "TARGET_INSTANCE_KEY": target["instance_key"],
                "SQLSERVER_HOST": target["host_name"],
                "SQLSERVER_PORT": target["port"],
                "SQLSERVER_CONNECTION_TIMEOUT": target["connection_timeout_seconds"],
            }
        )
        return MonitoringService(settings, PostgresRepository(settings.postgres_connection_string)).execute_pipeline()

    collect.expand(target=fetch_due_targets())


sqlserver_collection = sqlserver_collection()
