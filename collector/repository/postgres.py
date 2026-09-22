from datetime import datetime,timezone
from typing import Any
import psycopg
from psycopg.rows import dict_row
from collector.core.exceptions import DatabaseConnectionError,StagingLoadError

class PostgresRepository:
    def __init__(self,dsn:str): self._dsn=dsn
    def _get_connection(self):
        try: return psycopg.connect(self._dsn,row_factory=dict_row)
        except Exception as exc: raise DatabaseConnectionError(str(exc)) from exc
    def create_collection_run(self,instance_key:int,collector_name:str,collector_version:str)->int:
        with self._get_connection() as c, c.cursor() as cur:
            cur.execute("INSERT INTO monitoring.collection_run(instance_key,started_at,status,collector_name,collector_version) VALUES(%s,%s,'running',%s,%s) RETURNING collection_run_key",(instance_key,datetime.now(timezone.utc),collector_name,collector_version)); r=cur.fetchone(); c.commit(); return r['collection_run_key']
    def sync_databases(self,rows:list[dict[str,Any]])->None:
        with self._get_connection() as c, c.cursor() as cur:
            for r in rows:
                cur.execute("""INSERT INTO dimension.dim_database(instance_key,database_name,database_id,recovery_model,compatibility_level,is_system_database,is_active) VALUES(%s,%s,%s,%s,%s,%s,TRUE) ON CONFLICT(instance_key,database_name) DO UPDATE SET database_id=EXCLUDED.database_id,recovery_model=EXCLUDED.recovery_model,compatibility_level=EXCLUDED.compatibility_level,is_system_database=EXCLUDED.is_system_database,is_active=TRUE,updated_at=CURRENT_TIMESTAMP""",(r['instance_key'],r['database_name'],r['database_id'],r['recovery_model'],r['compatibility_level'],r['is_system_database']))
            c.commit()
    def log_collection_error(self,run:int,instance:int,error_type:str,error_message:str,metric_code:str|None=None)->None:
        try:
            with self._get_connection() as c,c.cursor() as cur:
                cur.execute("INSERT INTO monitoring.collection_error(collection_run_key,instance_key,metric_key,error_type,error_message) SELECT %s,%s,m.metric_key,%s,%s FROM (SELECT 1) x LEFT JOIN dimension.dim_metric m ON m.metric_code=%s",(run,instance,error_type,str(error_message),metric_code)); cur.execute("UPDATE monitoring.collection_run SET error_count=error_count+1 WHERE collection_run_key=%s",(run,)); c.commit()
        except Exception: pass
    def insert_staging_server_metrics(self,rows):
        if not rows:return 0
        with self._get_connection() as c,c.cursor() as cur:
            cur.executemany("INSERT INTO staging.server_metric(collection_run_key,instance_key,metric_code,collected_at,metric_value_numeric,metric_value_text,status,source_record_id) VALUES(%(collection_run_key)s,%(instance_key)s,%(metric_code)s,%(collected_at)s,%(metric_value_numeric)s,%(metric_value_text)s,%(status)s,%(source_record_id)s)",rows); c.commit(); return len(rows)
    def insert_staging_database_metrics(self,rows):
        if not rows:return 0
        with self._get_connection() as c,c.cursor() as cur:
            for r in rows:
                cur.execute("INSERT INTO staging.database_metric(collection_run_key,database_key,metric_code,collected_at,metric_value_numeric,metric_value_text,status,source_record_id) SELECT %s,d.database_key,%s,%s,%s,%s,%s,%s FROM dimension.dim_database d WHERE d.instance_key=%s AND d.database_name=%s AND d.is_active",(r['collection_run_key'],r['metric_code'],r['collected_at'],r['metric_value_numeric'],r['metric_value_text'],r['status'],r.get('source_record_id'),r['instance_key'],r['database_name']))
            c.commit(); return len(rows)
    def insert_specialized(self,kind,rows):
        if not rows:return 0
        with self._get_connection() as c,c.cursor() as cur:
            if kind=='wait':
                q="INSERT INTO fact.fact_wait_stat(instance_key,date_key,collected_at,wait_type,waiting_tasks_count,wait_time_ms,signal_wait_time_ms,max_wait_time_ms,resource_wait_time_ms,status,collection_run_key) VALUES(%s,TO_CHAR(%s AT TIME ZONE 'UTC','YYYYMMDD')::int,%s,%s,%s,%s,%s,%s,%s,%s,%s)"; vals=[(r['instance_key'],r['collected_at'],r['collected_at'],r['wait_type'],r['waiting_tasks_count'],r['wait_time_ms'],r['signal_wait_time_ms'],r['max_wait_time_ms'],r['resource_wait_time_ms'],r['status'],r['collection_run_key']) for r in rows]
            elif kind=='blocking':
                q="INSERT INTO fact.fact_blocking(instance_key,database_key,date_key,collected_at,blocking_session_id,blocked_session_id,blocking_status,wait_type,wait_time_ms,blocked_login_name,blocked_host_name,blocked_program_name,status,collection_run_key) SELECT %s,d.database_key,TO_CHAR(%s AT TIME ZONE 'UTC','YYYYMMDD')::int,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM dimension.dim_database d WHERE d.instance_key=%s AND d.database_name=%s"; vals=[(r['instance_key'],r['collected_at'],r['collected_at'],r['blocking_session_id'],r['blocked_session_id'],r.get('blocking_status'),r.get('wait_type'),r.get('wait_time_ms'),r.get('blocked_login_name'),r.get('blocked_host_name'),r.get('blocked_program_name'),r['status'],r['collection_run_key'],r['instance_key'],r.get('database_name')) for r in rows if r.get('database_name')]
            elif kind=='query':
                q="INSERT INTO fact.fact_query_stat(database_key,instance_key,date_key,collected_at,query_hash,query_plan_hash,sql_handle,plan_handle,query_text,execution_count,total_elapsed_ms,total_cpu_ms,total_logical_reads,total_logical_writes,total_physical_reads,last_elapsed_ms,last_cpu_ms,last_logical_reads,last_logical_writes,min_elapsed_ms,max_elapsed_ms,avg_elapsed_ms,avg_cpu_ms,avg_logical_reads,status,collection_run_key) SELECT d.database_key,%s,TO_CHAR(%s AT TIME ZONE 'UTC','YYYYMMDD')::int,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM dimension.dim_database d WHERE d.instance_key=%s AND d.database_name=%s"; vals=[(r['instance_key'],r['collected_at'],r['collected_at'],r.get('query_hash'),r.get('query_plan_hash'),r.get('sql_handle'),r.get('plan_handle'),r.get('query_text'),r.get('execution_count'),r.get('total_elapsed_ms'),r.get('total_cpu_ms'),r.get('total_logical_reads'),r.get('total_logical_writes'),r.get('total_physical_reads'),r.get('last_elapsed_ms'),r.get('last_cpu_ms'),r.get('last_logical_reads'),r.get('last_logical_writes'),r.get('min_elapsed_ms'),r.get('max_elapsed_ms'),r.get('avg_elapsed_ms'),r.get('avg_cpu_ms'),r.get('avg_logical_reads'),r['status'],r['collection_run_key'],r['instance_key'],r['database_name']) for r in rows]
            elif kind=='backup':
                q="INSERT INTO fact.fact_backup(instance_key,database_key,date_key,backup_start_at,backup_finish_at,backup_type,backup_status,duration_seconds,backup_size_bytes,compressed_backup_size_bytes,physical_device_type,backup_set_id,status,collection_run_key) SELECT %s,d.database_key,TO_CHAR(%s AT TIME ZONE 'UTC','YYYYMMDD')::int,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM dimension.dim_database d WHERE d.instance_key=%s AND d.database_name=%s"; vals=[(r['instance_key'],r['backup_start_at'],r['backup_start_at'],r['backup_finish_at'],r['backup_type'],r['backup_status'],r['duration_seconds'],r['backup_size_bytes'],r['compressed_backup_size_bytes'],r['physical_device_type'],r['backup_set_id'],r['status'],r['collection_run_key'],r['instance_key'],r['database_name']) for r in rows]
            elif kind=='agent':
                q="INSERT INTO fact.fact_sqlagent_job(instance_key,date_key,collected_at,job_id,job_name,run_id,run_start_at,run_finish_at,run_duration_seconds,run_status,message,sqlagent_job_enabled,status,collection_run_key) VALUES(%s,TO_CHAR(%s AT TIME ZONE 'UTC','YYYYMMDD')::int,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"; vals=[(r['instance_key'],r['collected_at'],r['collected_at'],r.get('job_id'),r['job_name'],r.get('run_id'),r.get('run_start_at'),r.get('run_finish_at'),r.get('run_duration_seconds'),r['run_status'],r.get('message'),r.get('sqlagent_job_enabled'),r['status'],r['collection_run_key']) for r in rows]
            elif kind=='deadlock':
                q="INSERT INTO fact.fact_deadlock(instance_key,date_key,occurred_at,deadlock_type,deadlock_graph,deadlock_hash,status,collection_run_key) VALUES(%s,TO_CHAR(%s AT TIME ZONE 'UTC','YYYYMMDD')::int,%s,%s,%s,%s,%s,%s) ON CONFLICT(instance_key,deadlock_hash) DO NOTHING"; vals=[(r['instance_key'],r['occurred_at'],r['occurred_at'],r['deadlock_type'],r['deadlock_graph'],r['deadlock_hash'],r['status'],r['collection_run_key']) for r in rows]
            else: return 0
            cur.executemany(q,vals); c.commit(); return len(vals)
    def execute_staging_load_procedures(self,run:int)->None:
        with self._get_connection() as c,c.cursor() as cur:
            try: cur.execute("CALL monitoring.sp_load_server_metrics(%s)",(run,));cur.execute("CALL monitoring.sp_load_database_metrics(%s)",(run,));c.commit()
            except Exception as exc: c.rollback();raise StagingLoadError(str(exc)) from exc
    def finalize_collection_run(self,run:int,requested:int,collected:int,records:int)->str:
        with self._get_connection() as c,c.cursor() as cur:
            cur.execute("SELECT error_count,started_at FROM monitoring.collection_run WHERE collection_run_key=%s",(run,)); r=cur.fetchone(); errors=r['error_count']; status='success' if errors==0 and collected==requested else ('partial' if collected>0 else 'failed'); finished=datetime.now(timezone.utc); cur.execute("UPDATE monitoring.collection_run SET finished_at=%s,status=%s,duration_seconds=%s,metrics_requested=%s,metrics_collected=%s,records_collected=%s WHERE collection_run_key=%s",(finished,status,(finished-r['started_at']).total_seconds(),requested,collected,records,run)); c.commit(); return status
