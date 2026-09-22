from collector.core.config import Settings
from collector.sqlserver.connection import SQLServerConnector
def test_sqlserver_target_contract():
    s=Settings(SQLSERVER_PASSWORD='p',POSTGRES_PASSWORD='pg')
    assert 'DRIVER={' in SQLServerConnector(s).build_connection_string()
