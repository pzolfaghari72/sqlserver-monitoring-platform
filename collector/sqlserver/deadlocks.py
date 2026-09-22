from datetime import datetime, timezone
import hashlib
import pyodbc

SQL = """
WITH SystemHealth AS (
    SELECT CAST(t.target_data AS XML) AS target_data
    FROM sys.dm_xe_session_targets AS t
    INNER JOIN sys.dm_xe_sessions AS s
        ON s.address = t.event_session_address
    WHERE s.name = N'system_health'
      AND t.target_name = N'ring_buffer'
)
SELECT
    event_data.value('(event/@timestamp)[1]', 'datetime2'),
    event_data.value('(event/data[@name="xml_report"]/value)[1]', 'nvarchar(max)')
FROM SystemHealth
CROSS APPLY target_data.nodes('//RingBufferTarget/event[@name="xml_deadlock_report"]') AS XEventData(event_data);
"""


def collect_deadlocks(conn: pyodbc.Connection, run_key: int, instance_key: int):
    cur = conn.cursor()
    cur.execute(SQL)
    now = datetime.now(timezone.utc)
    rows = []
    for occurred_at, graph in cur.fetchall():
        graph = graph or ""
        if not graph:
            continue
        deadlock_hash = hashlib.md5(graph.encode("utf-8", "ignore")).hexdigest()
        rows.append(
            {
                "collection_run_key": run_key,
                "instance_key": instance_key,
                "occurred_at": occurred_at.replace(tzinfo=timezone.utc) if occurred_at.tzinfo is None else occurred_at,
                "deadlock_type": "xml_deadlock_report",
                "deadlock_graph": graph,
                "deadlock_hash": deadlock_hash,
                "status": "success",
            }
        )
    return rows
