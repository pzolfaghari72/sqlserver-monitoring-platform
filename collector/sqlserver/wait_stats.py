"""Database engine thread wait states and contention telemetry."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

# Top 20 actionable wait states excluding benign background worker threads
WAIT_STATS_QUERY = """
SELECT TOP 20
    wait_type,
    waiting_tasks_count,
    wait_time_ms,
    signal_wait_time_ms,
    max_wait_time_ms,
    wait_time_ms - signal_wait_time_ms AS resource_wait_time_ms
FROM sys.dm_os_wait_stats WITH (NOLOCK)
WHERE wait_type NOT IN (
    'CLR_AUTO_EVENT', 'CLR_MANUAL_EVENT', 'CLR_SEMAPHORE',
    'LAZYWRITER_SLEEP', 'RESOURCE_QUEUE', 'SLEEP_TASK',
    'SLEEP_SYSTEMTASK', 'SQLTRACE_BUFFER_FLUSH', 'WAITFOR',
    'LOGMGR_QUEUE', 'CHECKPOINT_QUEUE', 'REQUEST_FOR_DEADLOCK_SEARCH',
    'XE_TIMER_EVENT', 'BROKER_TO_FLUSH', 'BROKER_TASK_STOP',
    'CLR_MONITOR', 'FT_IFTS_SCHEDULER_IDLE_WAIT', 'XE_DISPATCHER_WAIT',
    'XE_DISPATCHER_JOIN', 'DIRTY_PAGE_POLL', 'HADR_FILESTREAM_IOMGR_IOCOMPLETION'
)
ORDER BY wait_time_ms DESC;
"""


def collect_wait_stats(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Capture top instance-level wait states and queue metrics."""
    collected_at = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        cur.execute(WAIT_STATS_QUERY)
        for row in cur.fetchall():
            results.append(
                {
                    "collection_run_key": run_key,
                    "instance_key": instance_key,
                    "collected_at": collected_at,
                    "wait_type": row[0],
                    "waiting_tasks_count": int(row[1] or 0),
                    "wait_time_ms": int(row[2] or 0),
                    "signal_wait_time_ms": int(row[3] or 0),
                    "max_wait_time_ms": int(row[4] or 0),
                    "resource_wait_time_ms": int(row[5] or 0),
                    "status": "success",
                }
            )

    return results
