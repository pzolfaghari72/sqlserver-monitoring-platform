from functools import lru_cache
from typing import Generator, Literal
from urllib.parse import quote

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and .env.

    Responsibilities:
        - Validate application configuration.
        - Manage sensitive credentials using SecretStr.
        - Provide normalized connection strings for external systems.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # =========================================================
    # Collector Metadata
    # =========================================================

    COLLECTOR_NAME: str = Field(
        default="sqlserver-collector",
        min_length=1,
    )

    COLLECTOR_VERSION: str = Field(
        default="1.0.0",
        min_length=1,
    )

    # =========================================================
    # SQL Server - Target Database
    # =========================================================

    SQLSERVER_HOST: str = Field(
        ...,
        min_length=1,
    )

    SQLSERVER_PORT: int = Field(
        default=1433,
        ge=1,
        le=65535,
    )

    SQLSERVER_USER: str = Field(
        ...,
        min_length=1,
    )

    SQLSERVER_PASSWORD: SecretStr = Field(
        ...
    )

    SQLSERVER_DATABASE: str = Field(
        default="master",
        min_length=1,
    )

    SQLSERVER_INSTANCE_NAME: str = Field(
        default="MSSQLSERVER",
        min_length=1,
    )

    SQLSERVER_DRIVER: str = Field(
        default="ODBC Driver 18 for SQL Server",
        min_length=1,
    )

    SQLSERVER_ENCRYPT: Literal["yes", "no"] = "yes"

    SQLSERVER_TRUST_SERVER_CERTIFICATE: Literal["yes", "no"] = "yes"

    SQLSERVER_CONNECTION_TIMEOUT: int = Field(
        default=15,
        gt=0,
    )

    # =========================================================
    # PostgreSQL / TimescaleDB
    # Monitoring Storage Repository
    # =========================================================

    POSTGRES_HOST: str = Field(
        ...,
        min_length=1,
    )

    POSTGRES_PORT: int = Field(
        default=5432,
        ge=1,
        le=65535,
    )

    POSTGRES_DB: str = Field(
        ...,
        min_length=1,
    )

    POSTGRES_USER: str = Field(
        ...,
        min_length=1,
    )

    POSTGRES_PASSWORD: SecretStr = Field(
        ...
    )

    POSTGRES_SSLMODE: Literal[
        "disable",
        "allow",
        "prefer",
        "require",
        "verify-ca",
        "verify-full",
    ] = "prefer"

    # =========================================================
    # Application / Runtime
    # =========================================================

    TARGET_INSTANCE_KEY: int = Field(
        default=1,
        gt=0,
    )

    LOG_LEVEL: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = "INFO"

    # =========================================================
    # Internal Helpers
    # =========================================================

    @staticmethod
    def _escape_odbc_braced_value(value: str) -> str:
        """
        Escape a value that is enclosed in ODBC curly braces.

        ODBC connection-string values enclosed in braces escape a
        closing brace by doubling it.
        """
        return value.replace("}", "}}")

    # =========================================================
    # PostgreSQL Connection String
    # =========================================================

    @property
    def postgres_connection_string(self) -> str:
        """
        Build a PostgreSQL connection URI.

        Credentials are URL-encoded to safely handle special characters.
        """

        user = quote(
            self.POSTGRES_USER,
            safe="",
        )

        password = quote(
            self.POSTGRES_PASSWORD.get_secret_value(),
            safe="",
        )

        database = quote(
            self.POSTGRES_DB,
            safe="",
        )

        return (
            f"postgresql://{user}:{password}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{database}"
            f"?sslmode={self.POSTGRES_SSLMODE}"
        )

    # =========================================================
    # SQL Server ODBC Connection String
    # =========================================================

    @property
    def sqlserver_odbc_connection_string(self) -> str:
        """
        Build the SQL Server ODBC connection string.
        """

        user = self._escape_odbc_braced_value(
            self.SQLSERVER_USER
        )

        password = self._escape_odbc_braced_value(
            self.SQLSERVER_PASSWORD.get_secret_value()
        )

        driver = self._escape_odbc_braced_value(
            self.SQLSERVER_DRIVER
        )

        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={self.SQLSERVER_HOST},{self.SQLSERVER_PORT};"
            f"DATABASE={self.SQLSERVER_DATABASE};"
            f"UID={{{user}}};"
            f"PWD={{{password}}};"
            f"Encrypt={self.SQLSERVER_ENCRYPT};"
            f"TrustServerCertificate="
            f"{self.SQLSERVER_TRUST_SERVER_CERTIFICATE};"
            f"Connection Timeout={self.SQLSERVER_CONNECTION_TIMEOUT};"
        )


# =============================================================
# Settings Factory
# =============================================================

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the application-wide Settings instance.

    Settings are created once and cached for the lifetime of the
    process.
    """
    return Settings()