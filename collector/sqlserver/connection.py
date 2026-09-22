import logging
from contextlib import contextmanager
from typing import Generator
from collector.core.config import Settings

logger = logging.getLogger(__name__)

class SQLServerConnector:
    def __init__(self, settings: Settings): self.settings = settings
    def build_connection_string(self) -> str:
        return (f"DRIVER={{{self.settings.SQLSERVER_DRIVER}}};SERVER={self.settings.SQLSERVER_HOST},{self.settings.SQLSERVER_PORT};"
                f"DATABASE={self.settings.SQLSERVER_DATABASE};UID={self.settings.SQLSERVER_USER};PWD={self.settings.SQLSERVER_PASSWORD};"
                f"Encrypt={self.settings.SQLSERVER_ENCRYPT};TrustServerCertificate={self.settings.SQLSERVER_TRUST_SERVER_CERTIFICATE};")
    @contextmanager
    def get_connection(self) -> Generator[object,None,None]:
        import pyodbc
        conn=None
        try:
            conn=pyodbc.connect(self.build_connection_string(), timeout=self.settings.SQLSERVER_CONNECTION_TIMEOUT)
            yield conn
        finally:
            if conn is not None: conn.close()

def get_sql_connection(settings: Settings):
    return SQLServerConnector(settings).get_connection()
