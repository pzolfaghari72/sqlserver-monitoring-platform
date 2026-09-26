"""Deadlock graph extraction from Extended Events system_health ring buffer."""

from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

DEADLOCK_RING_BUFFER_QUERY = """
WITH SystemHealth AS (
    SELECT CAST(t.target_data AS XML) AS target_data
    FROM sys.dm_xe_session_targets AS t WITH (NOLOCK)
    INNER JOIN sys.dm_xe_sessions AS s WITH (NOLOCK)
        ON s.address = t.event_session_address
    WHERE s.name = N'system_health'
      AND t.target_name = N'ring_buffer'
)
SELECT
    event_data.value('(event/@timestamp)[1]', 'datetime2') AS occurred_at,
    event_data.value('(event/data[@name="xml_report"]/value)[1]', 'nvarchar(max)') AS xml_report
FROM SystemHealth
CROSS APPLY target_data.nodes('//RingBufferTarget/event[@name="xml_deadlock_report"]') AS XEventData(event_data);
"""


def collect_deadlocks(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Collect xml_deadlock_reports from system_health ring buffer."""
    results: List[Dict[str, Any]] = []

    try:
        with conn.cursor() as cur:
            cur.execute(DEADLOCK_RING_BUFFER_QUERY)
            for occurred_at, graph in cur.fetchall():
                if not graph or not occurred_at:
                    continue

                graph_str = graph.strip()
                deadlock_hash = hashlib.md5(graph_str.encode("utf-8", errors="ignore")).hexdigest()

                if occurred_at.tzinfo is None:
                    occurred_at = occurred_at.replace(tzinfo=timezone.utc)

                results.append(
                    {
                        "collection_run_key": run_key,
                        "instance_key": instance_key,
                        "occurred_at": occurred_at,
                        "deadlock_type": "xml_deadlock_report",
                        "deadlock_graph": graph_str,
                        "deadlock_hash": deadlock_hash,
                        "status": "success",
                    }
                )
    except Exception as exc:
        logger.warning("Could not read system_health ring buffer for deadlocks: %s", exc)

    return results
