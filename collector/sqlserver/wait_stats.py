from datetime import datetime, timezone
import pyodbc
SQL="""SELECT TOP 20 wait_type,waiting_tasks_count,wait_time_ms,signal_wait_time_ms,max_wait_time_ms,wait_time_ms-signal_wait_time_ms FROM sys.dm_os_wait_stats WHERE wait_type NOT IN ('SLEEP_TASK','BROKER_TASK_STOP','BROKER_TO_FLUSH','SQLTRACE_BUFFER_FLUSH','CLR_AUTO_EVENT','CLR_MANUAL_EVENT','REQUEST_FOR_DEADLOCK_SEARCH','XE_TIMER_EVENT','XE_DISPATCHER_WAIT','FT_IFTS_SCHEDULER_IDLE_WAIT') ORDER BY wait_time_ms DESC"""
def collect_wait_stats(conn,run_key,instance_key):
    cur=conn.cursor();cur.execute(SQL);now=datetime.now(timezone.utc);out=[]
    for r in cur.fetchall(): out.append({'collection_run_key':run_key,'instance_key':instance_key,'collected_at':now,'wait_type':r[0],'waiting_tasks_count':int(r[1]),'wait_time_ms':int(r[2]),'signal_wait_time_ms':int(r[3]),'max_wait_time_ms':int(r[4]),'resource_wait_time_ms':int(r[5]),'status':'success'})
    return out
