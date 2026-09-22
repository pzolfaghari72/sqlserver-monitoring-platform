from datetime import datetime, timezone
from typing import Any
import pyodbc

QUERIES={
'CPU_UTILIZATION': """SELECT TOP 1 CAST(record.value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]','int') AS float) FROM (SELECT CAST(record AS xml) record FROM sys.dm_os_ring_buffers WHERE ring_buffer_type=N'RING_BUFFER_SCHEDULER_MONITOR' AND record LIKE '%<SystemHealth>%') x ORDER BY record.value('(./Record/@id)[1]','bigint') DESC""",
'PAGE_LIFE_EXPECTANCY': """SELECT TOP 1 CAST(cntr_value AS float) FROM sys.dm_os_performance_counters WHERE counter_name='Page life expectancy' AND object_name LIKE '%Buffer Manager%'""",
'BATCH_REQUESTS_PER_SEC': """SELECT TOP 1 CAST(cntr_value AS float) FROM sys.dm_os_performance_counters WHERE counter_name='Batch Requests/sec' AND object_name LIKE '%SQL Statistics%'""",
'MEMORY_UTILIZATION': """SELECT TOP 1 CAST(100.0 * (total_physical_memory_kb-available_physical_memory_kb) / NULLIF(total_physical_memory_kb,0) AS float) FROM sys.dm_os_sys_memory""",
}

def collect_server_metrics(conn: pyodbc.Connection, run_key: int, instance_key: int) -> list[dict[str,Any]]:
    now=datetime.now(timezone.utc); out=[]; cur=conn.cursor()
    for code,sql in QUERIES.items():
        cur.execute(sql); row=cur.fetchone()
        if row and row[0] is not None:
            out.append({'collection_run_key':run_key,'instance_key':instance_key,'metric_code':code,'collected_at':now,'metric_value_numeric':float(row[0]),'metric_value_text':None,'status':'success','source_record_id':None})
    return out
