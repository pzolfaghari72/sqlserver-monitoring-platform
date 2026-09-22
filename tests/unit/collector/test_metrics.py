from collector.core.config import Settings
from collector.sqlserver.connection import SQLServerConnector
def test_sql_connection_string():
    s=Settings(SQLSERVER_HOST='sqlserver',SQLSERVER_PORT=1444,SQLSERVER_USER='u',SQLSERVER_PASSWORD='p',POSTGRES_PASSWORD='pg')
    c=SQLServerConnector(s).build_connection_string()
    assert 'SERVER=sqlserver,1444;' in c and 'UID=u;' in c and 'PWD=p;' in c
