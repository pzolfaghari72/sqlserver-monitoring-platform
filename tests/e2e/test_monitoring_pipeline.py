from pathlib import Path
def test_end_to_end_components_exist():
    root=Path(__file__).parents[2]
    for p in ['docker-compose.yml','scripts/bootstrap/init_database.sh','collector/collector.py','airflow/dags/sqlserver_collection.py','grafana/provisioning/datasources/postgres.yml']:
        assert (root/p).exists()
