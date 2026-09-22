from functools import lru_cache
from urllib.parse import quote

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    COLLECTOR_NAME: str = "sqlserver-collector"
    COLLECTOR_VERSION: str = "1.0.0"
    SQLSERVER_HOST: str = "sqlserver"
    SQLSERVER_PORT: int = 1433
    SQLSERVER_USER: str = "sa"
    SQLSERVER_PASSWORD: str = Field(...)
    SQLSERVER_DATABASE: str = "master"
    SQLSERVER_INSTANCE_NAME: str = "MSSQLSERVER"
    SQLSERVER_DRIVER: str = "ODBC Driver 18 for SQL Server"
    SQLSERVER_ENCRYPT: str = "yes"
    SQLSERVER_TRUST_SERVER_CERTIFICATE: str = "yes"
    SQLSERVER_CONNECTION_TIMEOUT: int = 15
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "sqlserver_monitoring"
    POSTGRES_USER: str = "monitoring_user"
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_SSLMODE: str = "prefer"
    TARGET_INSTANCE_KEY: int = 1
    LOG_LEVEL: str = "INFO"
    @property
    def postgres_connection_string(self) -> str:
        user = quote(self.POSTGRES_USER, safe="")
        password = quote(self.POSTGRES_PASSWORD, safe="")
        return f"postgresql://{user}:{password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}?sslmode={self.POSTGRES_SSLMODE}"

@lru_cache
def get_settings() -> Settings:
    return Settings()
