"""Top resource-intensive query statistics collector."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

QUERY_STATS_QUERY = """
SELECT TOP 20
    CONVERT(bigint, qs.query_hash) AS query_hash,
    CONVERT(bigint, qs.query_plan_hash) AS query_plan_hash,
    qs.execution_count,
    qs.total_elapsed_time,
    qs.total_worker_time,
    qs.total_logical_reads,
    qs.total_logical_writes,
    qs.total_physical_reads,
    qs.last_elapsed_time,
    qs.last_worker_time,
    qs.last_logical_reads,
    qs.last_logical_writes,
    qs.min_elapsed_time,
    qs.max_elapsed_time,
    qs.total_elapsed_time / NULLIF(qs.execution_count, 0) AS avg_elapsed_time,
    qs.total_worker_time / NULLIF(qs.execution_count, 0) AS avg_worker_time,
    qs.total_logical_reads / NULLIF(qs.execution_count, 0) AS avg_logical_reads,
    DB_NAME(st.dbid) AS database_name,
    SUBSTRING(st.text, (qs.statement_start_offset / 2) + 1,
        ((CASE qs.statement_end_offset
            WHEN -1 THEN DATALENGTH(st.text)
            ELSE qs.statement_end_offset
         END - qs.statement_start_offset) / 2) + 1
    ) AS query_text,
    CONVERT(varchar(128), qs.sql_handle, 2) AS sql_handle,
    CONVERT(varchar(128), qs.plan_handle, 2) AS plan_handle
FROM sys.dm_exec_query_stats qs WITH (NOLOCK)
CROSS APPLY sys.dm_exec_sql_text(qs.sql_handle) st
ORDER BY qs.total_worker_time DESC;
"""


def collect_query_metrics(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Capture top CPU intensive queries along with execution profiles."""
    collected_at = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        cur.execute(QUERY_STATS_QUERY)
        for row in cur.fetchall():
            db_name = row[17]
            if not db_name:
                continue

            results.append(
                {
                    "collection_run_key": run_key,
                    "instance_key": instance_key,
                    "collected_at": collected_at,
                    "query_hash": row[0],
                    "query_plan_hash": row[1],
                    "execution_count": int(row[2] or 0),
                    "total_elapsed_ms": float((row[3] or 0) / 1000.0),
                    "total_cpu_ms": float((row[4] or 0) / 1000.0),
                    "total_logical_reads": int(row[5] or 0),
                    "total_logical_writes": int(row[6] or 0),
                    "total_physical_reads": int(row[7] or 0),
                    "last_elapsed_ms": float((row[8] or 0) / 1000.0),
                    "last_cpu_ms": float((row[9] or 0) / 1000.0),
                    "last_logical_reads": int(row[10] or 0),
                    "last_logical_writes": int(row[11] or 0),
                    "min_elapsed_ms": float((row[12] or 0) / 1000.0),
                    "max_elapsed_ms": float((row[13] or 0) / 1000.0),
                    "avg_elapsed_ms": float((row[14] or 0) / 1000.0),
                    "avg_cpu_ms": float((row[15] or 0) / 1000.0),
                    "avg_logical_reads": float(row[16] or 0.0),
                    "database_name": db_name,
                    "query_text": str(row[18])[:4000] if row[18] else None,
                    "sql_handle": row[19],
                    "plan_handle": row[20],
                    "status": "success",
                }
            )

    return results
