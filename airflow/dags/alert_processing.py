"""Alert Processing DAG.

Evaluates monitoring thresholds and generates operational alerts
for newly completed telemetry collection runs across all monitored instances.
"""

from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger("airflow.task")

# Maximum number of pending runs to process in a single DAG iteration
MAX_BATCH_SIZE = 20

# Query to find collection runs that have completed successfully but haven't had alerts evaluated yet
FETCH_PENDING_RUNS_QUERY = f"""
SELECT 
    cr.collection_run_key,
    cr.instance_key,
    cr.status,
    cr.finished_at
FROM monitoring.collection_run cr
WHERE cr.status IN ('success', 'partial')
  AND cr.alerts_processed_at IS NULL
ORDER BY cr.finished_at ASC
LIMIT {MAX_BATCH_SIZE};
"""

UPDATE_RUN_PROCESSED_QUERY = """
UPDATE monitoring.collection_run
SET alerts_processed_at = NOW()
WHERE collection_run_key = %(collection_run_key)s;
"""


@dag(
    dag_id="alert_processing",
    schedule="*/2 * * * *",  # Evaluates alerts every 2 minutes
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "owner": "data_platform",
        "retries": 1,
        "retry_delay": timedelta(seconds=20),
    },
    tags=["sqlserver", "alerts", "monitoring"],
)
def alert_processing_dag():

    @task
    def fetch_pending_runs() -> List[Dict[str, Any]]:
        """Identify completed collection runs that require alert evaluation."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        rows = hook.get_records(FETCH_PENDING_RUNS_QUERY)

        pending_runs = [
            {
                "collection_run_key": row[0],
                "instance_key": row[1],
                "status": row[2],
                "finished_at": row[3].isoformat() if row[3] else None,
            }
            for row in rows
        ]

        logger.info("Found %d collection runs pending alert processing.", len(pending_runs))
        return pending_runs

    @task
    def evaluate_alerts(pending_runs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Execute the alert evaluation stored procedure for each pending run."""
        if not pending_runs:
            logger.info("No pending collection runs to process.")
            return {"processed": 0, "failed": 0}

        hook = PostgresHook(postgres_conn_id="postgres_default")
        conn = hook.get_conn()
        
        success_count = 0
        failure_count = 0

        with conn.cursor() as cursor:
            for run in pending_runs:
                run_key = run["collection_run_key"]
                instance_key = run["instance_key"]
                try:
                    logger.info("Evaluating alerts for collection_run_key=%s (instance_key=%s)", run_key, instance_key)
                    
                    # Execute alert evaluation procedure
                    cursor.execute("CALL monitoring.sp_process_alerts(%s);", (run_key,))
                    
                    # Mark collection run as processed
                    cursor.execute(UPDATE_RUN_PROCESSED_QUERY, {"collection_run_key": run_key})
                    
                    conn.commit()
                    success_count += 1
                except Exception as exc:
                    conn.rollback()
                    failure_count += 1
                    logger.exception(
                        "Failed to process alerts for collection_run_key=%s: %s",
                        run_key,
                        exc,
                    )

        logger.info(
            "Alert evaluation summary: %d succeeded, %d failed out of %d total.",
            success_count,
            failure_count,
            len(pending_runs),
        )

        if failure_count > 0 and success_count == 0:
            raise RuntimeError(f"All {failure_count} alert processing attempts failed.")

        return {"processed": success_count, "failed": failure_count}

    # Task sequence
    pending = fetch_pending_runs()
    evaluate_alerts(pending)


alert_processing = alert_processing_dag()
