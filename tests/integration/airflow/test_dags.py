import pytest

def test_dag_modules_importable():
    try:
        import airflow.decorators  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip('Apache Airflow is not installed in the local test environment')
    import airflow.dags.sqlserver_collection
    import airflow.dags.sqlserver_monitoring
    import airflow.dags.alert_processing
