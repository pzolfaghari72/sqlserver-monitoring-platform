from pathlib import Path
def test_required_database_scripts_exist():
    root=Path(__file__).parents[3]
    required=['db/init/002_create_schemas.sql','db/dimensions/dim_server.sql','db/dimensions/dim_instance.sql','db/facts/fact_server_metric.sql','db/procedures/sp_load_server_metrics.sql']
    assert all((root/p).exists() for p in required)
