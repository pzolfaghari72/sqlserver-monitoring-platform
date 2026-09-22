from datetime import datetime,timedelta
from airflow.decorators import dag,task
from airflow.providers.postgres.hooks.postgres import PostgresHook
@dag(dag_id="alert_processing",schedule="*/2 * * * *",start_date=datetime(2026,1,1),catchup=False,max_active_runs=1,default_args={"owner":"data_platform","retries":1,"retry_delay":timedelta(seconds=20)},tags=["alerts"])
def alert_processing():
    @task
    def process():
        hook=PostgresHook(postgres_conn_id='postgres_default');run=hook.get_first("SELECT collection_run_key FROM monitoring.collection_run WHERE status IN ('success','partial') ORDER BY finished_at DESC LIMIT 1")
        if run: hook.run("CALL monitoring.sp_process_alerts(%s)",parameters=(run[0],))
    process()
alert_processing=alert_processing()
