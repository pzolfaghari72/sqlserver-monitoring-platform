from collector.core.config import Settings
def test_postgres_dsn():
    s=Settings(SQLSERVER_PASSWORD='s',POSTGRES_PASSWORD='p',POSTGRES_HOST='db',POSTGRES_PORT=5433,POSTGRES_DB='m',POSTGRES_USER='u')
    assert 'u:p@db:5433/m' in s.postgres_connection_string
