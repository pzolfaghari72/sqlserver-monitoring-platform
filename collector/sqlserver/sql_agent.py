from datetime import datetime, timezone
import pyodbc
SQL="""SELECT j.job_id,j.name,j.enabled,jh.instance_id,jh.run_status,msdb.dbo.agent_datetime(jh.run_date,jh.run_time),((jh.run_duration/10000)*3600+((jh.run_duration%10000)/100)*60+(jh.run_duration%100)),jh.message FROM msdb.dbo.sysjobs j JOIN msdb.dbo.sysjobhistory jh ON j.job_id=jh.job_id WHERE jh.step_id=0 AND jh.run_date>=CONVERT(int,CONVERT(varchar(8),DATEADD(day,-1,GETDATE()),112))"""
def collect_agent_metrics(conn,run_key,instance_key):
    cur=conn.cursor();cur.execute(SQL);now=datetime.now(timezone.utc);out=[]
    for r in cur.fetchall(): out.append({'collection_run_key':run_key,'instance_key':instance_key,'collected_at':now,'job_id':str(r[0]),'job_name':r[1],'sqlagent_job_enabled':bool(r[2]),'run_id':int(r[3]) if r[3] else None,'run_status':'SUCCESS' if r[4]==1 else 'FAILED','run_start_at':r[5],'run_finish_at':None,'run_duration_seconds':float(r[6] or 0),'message':r[7],'status':'success'})
    return out
