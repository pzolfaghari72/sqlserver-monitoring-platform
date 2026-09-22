# ==============================================================================
# File: collector/sqlserver/__init__.py
# Description: Export SQL Server connection factory and collectors
# ==============================================================================
from .connection import get_sql_connection

__all__ = ["get_sql_connection"]
