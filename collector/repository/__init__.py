# ==============================================================================
# File: collector/repository/__init__.py
# Description: Repository package export for data persistence operations
# ==============================================================================
from .postgres import PostgresRepository

__all__ = ["PostgresRepository"]
