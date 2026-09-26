"""Active blocking chains and lock contention collector."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

BLOCKING_SESSIONS_QUERY = """
SELECT
    r.blocking_session_id,
    r.session_id AS blocked_session_id,
    r.wait_type,
    r.wait_time AS wait_time_ms,
    ISNULL(DB_NAME(r.database_id), 'UNKNOWN') AS database_name,
    s.login_name AS blocked_login_name,
    s.host_name AS blocked_host_name,
    s.program_name AS blocked_program_name,
    r.status AS blocking_status
FROM sys.dm_exec_requests r WITH (NOLOCK)
INNER JOIN sys.dm_exec_sessions s WITH (NOLOCK)
    ON s.session_id = r.session_id
WHERE r.blocking_session_id <> 0;
"""


def collect_blocking_metrics(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Capture currently blocked requests and blocker session headers."""
    collected_at = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        cur.execute(BLOCKING_SESSIONS_QUERY)
        for row in cur.fetchall():
            results.append(
                {
                    "collection_run_key": run_key,
                    "instance_key": instance_key,
                    "collected_at": collected_at,
                    "blocking_session_id": int(row[0]),
                    "blocked_session_id": int(row[1]),
                    "wait_type": row[2],
                    "wait_time_ms": int(row[3] or 0),
                    "database_name": row[4],
                    "blocked_login_name": row[5],
                    "blocked_host_name": row[6],
                    "blocked_program_name": row[7],
                    "blocking_status": row[8],
                    "status": "success",
                }
            )

    return results
