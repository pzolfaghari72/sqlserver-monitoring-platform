from app.schemas.targets import TargetResponse
def test_target_response():
    x=TargetResponse(target_id=1,instance_key=2,instance_name='MSSQLSERVER',host_name='sqlserver',port=1433,environment='development',collection_interval_seconds=60,is_enabled=True,connection_timeout_seconds=10,command_timeout_seconds=30,max_retry_count=3,priority=100,created_at='2026-09-21T00:00:00Z',updated_at='2026-09-21T00:00:00Z')
    assert x.instance_name=='MSSQLSERVER'
