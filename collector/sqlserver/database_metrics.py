from datetime import datetime, timezone
from typing import Any
import pyodbc

SQL="""SELECT d.name,'DATABASE_SIZE',CAST(SUM(CASE WHEN mf.type_desc='ROWS' THEN mf.size ELSE 0 END)*8.0/1024.0 AS float),d.state_desc FROM sys.databases d JOIN sys.master_files mf ON mf.database_id=d.database_id GROUP BY d.name,d.state_desc"""
LOG="""SELECT d.name,'LOG_USAGE',CAST(SUM(CASE WHEN mf.type_desc='LOG' THEN mf.size ELSE 0 END)*8.0/1024.0 AS float),NULL FROM sys.databases d JOIN sys.master_files mf ON mf.database_id=d.database_id GROUP BY d.name"""

def collect_database_metrics(conn: pyodbc.Connection, run_key:int, instance_key:int)->list[dict[str,Any]]:
    now=datetime.now(timezone.utc); out=[]; cur=conn.cursor()
    for sql in (SQL,LOG):
        cur.execute(sql)
        for r in cur.fetchall(): out.append({'collection_run_key':run_key,'instance_key':instance_key,'database_name':r[0],'metric_code':r[1],'collected_at':now,'metric_value_numeric':float(r[2] or 0),'metric_value_text':r[3],'status':'success','source_record_id':r[0]})
    return out

def sync_databases(conn: pyodbc.Connection, run_key:int, instance_key:int)->list[dict[str,Any]]:
    cur=conn.cursor(); cur.execute("SELECT name,database_id,recovery_model_desc,compatibility_level,CASE WHEN database_id<=4 THEN 1 ELSE 0 END FROM sys.databases")
    return [{'instance_key':instance_key,'database_name':r[0],'database_id':int(r[1]),'recovery_model':r[2],'compatibility_level':int(r[3]),'is_system_database':bool(r[4])} for r in cur.fetchall()]
