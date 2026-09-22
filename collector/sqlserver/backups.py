from datetime import datetime, timezone
import pyodbc
SQL="""SELECT d.name,MAX(b.backup_start_date),MAX(b.backup_finish_date),CASE WHEN MAX(b.backup_finish_date) IS NULL THEN 999999 ELSE DATEDIFF(SECOND,MAX(b.backup_finish_date),GETDATE()) END,MAX(b.backup_size),MAX(b.compressed_backup_size),MAX(b.type),MAX(b.backup_set_id) FROM sys.databases d LEFT JOIN msdb.dbo.backupset b ON b.database_name=d.name AND b.type='D' GROUP BY d.name"""
def collect_backup_metrics(conn,run_key,instance_key):
    cur=conn.cursor();cur.execute(SQL);now=datetime.now(timezone.utc);out=[]
    for r in cur.fetchall():
        if r[1] is None: continue
        out.append({'collection_run_key':run_key,'instance_key':instance_key,'collected_at':now,'database_name':r[0],'backup_start_at':r[1],'backup_finish_at':r[2],'backup_type':'FULL','backup_status':'SUCCESS','duration_seconds':float((r[2]-r[1]).total_seconds()) if r[2] else None,'backup_size_bytes':int(r[4] or 0),'compressed_backup_size_bytes':int(r[5] or 0),'backup_set_id':int(r[7]) if r[7] else None,'physical_device_type':None,'status':'success'})
    return out
