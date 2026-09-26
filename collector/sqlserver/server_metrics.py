"""Host and instance-level system resource utilization metrics."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

SERVER_METRIC_QUERIES: Dict[str, str] = {
    "CPU_UTILIZATION": """
        SELECT TOP 1
            CAST(record.value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') AS float)
        FROM (
            SELECT CAST(record AS xml) AS record
            FROM sys.dm_os_ring_buffers WITH (NOLOCK)
            WHERE ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR'
              AND record LIKE '%<SystemHealth>%'
        ) x
        ORDER BY record.value('(./Record/@id)[1]', 'bigint') DESC;
    """,
    "PAGE_LIFE_EXPECTANCY": """
        SELECT TOP 1 CAST(cntr_value AS float)
        FROM sys.dm_os_performance_counters WITH (NOLOCK)
        WHERE counter_name = 'Page life expectancy'
          AND object_name LIKE '%Buffer Manager%';
    """,
    "BATCH_REQUESTS_PER_SEC": """
        SELECT TOP 1 CAST(cntr_value AS float)
        FROM sys.dm_os_performance_counters WITH (NOLOCK)
        WHERE counter_name = 'Batch Requests/sec'
          AND object_name LIKE '%SQL Statistics%';
    """,
    "MEMORY_UTILIZATION": """
        SELECT TOP 1
            CAST(100.0 * (total_physical_memory_kb - available_physical_memory_kb) / NULLIF(total_physical_memory_kb, 0) AS float)
        FROM sys.dm_os_sys_memory WITH (NOLOCK);
    """,
}


def collect_server_metrics(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Query OS performance counters and hardware consumption stats."""
    collected_at = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        for metric_code, sql_stmt in SERVER_METRIC_QUERIES.items():
            try:
                cur.execute(sql_stmt)
                row = cur.fetchone()
                if row and row[0] is not None:
                    results.append(
                        {
                            "collection_run_key": run_key,
                            "instance_key": instance_key,
                            "metric_code": metric_code,
                            "collected_at": collected_at,
                            "metric_value_numeric": float(row[0]),
                            "metric_value_text": None,
                            "status": "success",
                            "source_record_id": None,
                        }
                    )
            except Exception as exc:
                logger.warning("Failed executing server metric %s: %s", metric_code, exc)

    return results
