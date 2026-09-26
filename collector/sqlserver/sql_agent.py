"""SQL Server Agent job execution telemetry collector."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

# Retrieves jobs run within the last 24 hours
AGENT_JOBS_QUERY = """
SELECT
    j.job_id,
    j.name AS job_name,
    j.enabled AS sqlagent_job_enabled,
    jh.instance_id AS run_id,
    jh.run_status,
    msdb.dbo.agent_datetime(jh.run_date, jh.run_time) AS run_start_at,
    ((jh.run_duration / 10000) * 3600 + ((jh.run_duration % 10000) / 100) * 60 + (jh.run_duration % 100)) AS run_duration_seconds,
    jh.message
FROM msdb.dbo.sysjobs j WITH (NOLOCK)
INNER JOIN msdb.dbo.sysjobhistory jh WITH (NOLOCK)
    ON j.job_id = jh.job_id
WHERE jh.step_id = 0 -- Full job outcome
  AND jh.run_date >= CONVERT(int, CONVERT(varchar(8), DATEADD(day, -1, GETDATE()), 112));
"""


def collect_agent_metrics(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Capture execution status of recently invoked SQL Agent jobs."""
    collected_at = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        cur.execute(AGENT_JOBS_QUERY)
        for row in cur.fetchall():
            start_at = row[5]
            duration_sec = float(row[6] or 0.0)

            finish_at = None
            if start_at:
                finish_at = start_at + timedelta(seconds=duration_sec)

            results.append(
                {
                    "collection_run_key": run_key,
                    "instance_key": instance_key,
                    "collected_at": collected_at,
                    "job_id": str(row[0]),
                    "job_name": row[1],
                    "sqlagent_job_enabled": bool(row[2]),
                    "run_id": int(row[3]) if row[3] else None,
                    "run_status": "SUCCESS" if row[4] == 1 else "FAILED",
                    "run_start_at": start_at,
                    "run_finish_at": finish_at,
                    "run_duration_seconds": duration_sec,
                    "message": str(row[7])[:1000] if row[7] else None,
                    "status": "success",
                }
            )

    return results
