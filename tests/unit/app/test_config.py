from app.core.config import AppSettings
def test_database_url():
    s=AppSettings(APP_SECRET_KEY='x',POSTGRES_HOST='db',POSTGRES_PORT=5433,POSTGRES_DB='m',POSTGRES_USER='u',POSTGRES_PASSWORD='p')
    assert s.database_url=='postgresql://u:p@db:5433/m'
