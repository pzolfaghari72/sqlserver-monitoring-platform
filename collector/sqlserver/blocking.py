from datetime import datetime, timezone
import pyodbc
SQL="""SELECT r.blocking_session_id,r.session_id,r.wait_type,r.wait_time,DB_NAME(r.database_id),s.login_name,s.host_name,s.program_name,r.command FROM sys.dm_exec_requests r JOIN sys.dm_exec_sessions s ON s.session_id=r.session_id WHERE r.blocking_session_id<>0"""
def collect_blocking_metrics(conn,run_key,instance_key):
    cur=conn.cursor();cur.execute(SQL);now=datetime.now(timezone.utc);out=[]
    for r in cur.fetchall(): out.append({'collection_run_key':run_key,'instance_key':instance_key,'collected_at':now,'blocking_session_id':int(r[0]),'blocked_session_id':int(r[1]),'wait_type':r[2],'wait_time_ms':int(r[3] or 0),'database_name':r[4],'blocked_login_name':r[5],'blocked_host_name':r[6],'blocked_program_name':r[7],'blocking_status':r[8],'status':'success'})
    return out
