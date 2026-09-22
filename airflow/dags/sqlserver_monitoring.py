from datetime import datetime,timedelta
from airflow.decorators import dag,task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from collector.core.config import get_settings
from collector.sqlserver.connection import get_sql_connection

@dag(dag_id="sqlserver_monitoring",schedule="*/2 * * * *",start_date=datetime(2026,1,1),catchup=False,max_active_runs=1,default_args={"owner":"data_platform","retries":1,"retry_delay":timedelta(seconds=20)},tags=["sqlserver","health"])
def sqlserver_monitoring():
    @task
    def check_instances():
        hook=PostgresHook(postgres_conn_id="postgres_default");rows=hook.get_records("SELECT i.instance_key,s.host_name,i.port FROM config.monitoring_target t JOIN dimension.dim_instance i ON i.instance_key=t.instance_key JOIN dimension.dim_server s ON s.server_key=i.server_key WHERE t.enabled AND i.is_active AND s.is_active")
        base=get_settings()
        for key,host,port in rows:
            settings=base.model_copy(update={"TARGET_INSTANCE_KEY":key,"SQLSERVER_HOST":host,"SQLSERVER_PORT":port or 1433})
            try:
                with get_sql_connection(settings): status,message='healthy','SQL Server connection succeeded'
            except Exception as exc: status,message='unhealthy',str(exc)
            hook.run("""INSERT INTO monitoring.system_health(component_name,component_type,status,host_name,last_heartbeat_at,last_success_at,last_error_at,message,consecutive_failures,updated_at) VALUES(%s,'sqlserver_instance',%s,%s,NOW(),CASE WHEN %s='healthy' THEN NOW() END,CASE WHEN %s='unhealthy' THEN NOW() END,%s,CASE WHEN %s='healthy' THEN 0 ELSE 1 END,NOW()) ON CONFLICT(component_name) DO UPDATE SET status=EXCLUDED.status,host_name=EXCLUDED.host_name,last_heartbeat_at=NOW(),last_success_at=CASE WHEN EXCLUDED.status='healthy' THEN NOW() ELSE monitoring.system_health.last_success_at END,last_error_at=CASE WHEN EXCLUDED.status='unhealthy' THEN NOW() ELSE monitoring.system_health.last_error_at END,message=EXCLUDED.message,consecutive_failures=CASE WHEN EXCLUDED.status='healthy' THEN 0 ELSE monitoring.system_health.consecutive_failures+1 END,updated_at=NOW()""", parameters=(f'sqlserver:{key}',status,host,status,status,message,status))
    check_instances()
sqlserver_monitoring=sqlserver_monitoring()
