from datetime import datetime,timedelta
from airflow.decorators import dag,task
from airflow.providers.postgres.hooks.postgres import PostgresHook
@dag(dag_id="data_quality",schedule="0 2 * * *",start_date=datetime(2026,1,1),catchup=False,max_active_runs=1,default_args={"owner":"data_platform","retries":1,"retry_delay":timedelta(minutes=2)},tags=["data-quality","maintenance"])
def data_quality():
    @task
    def validate_and_cleanup():
        h=PostgresHook(postgres_conn_id='postgres_default')
        for q in ["DELETE FROM staging.server_metric WHERE loaded_at < NOW()-INTERVAL '3 days'","DELETE FROM staging.database_metric WHERE loaded_at < NOW()-INTERVAL '3 days'"]: h.run(q)
        orphan=h.get_first("SELECT COUNT(*) FROM fact.fact_server_metric f LEFT JOIN dimension.dim_instance i ON i.instance_key=f.instance_key WHERE i.instance_key IS NULL")[0]
        if orphan: raise ValueError(f'Orphan fact rows: {orphan}')
    validate_and_cleanup()
data_quality=data_quality()
