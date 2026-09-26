class CollectorBaseException(Exception):
    """Base exception for all collector errors."""

class DatabaseConnectionError(CollectorBaseException):
    """Raised when connection to target SQL Server or repository DB fails."""

class QueryExecutionError(CollectorBaseException):
    """Raised when executing extraction queries or DMVs fails."""

class StagingLoadError(CollectorBaseException):
    """Raised when batch data loading or ingestion into repository fails."""

class ConfigurationError(CollectorBaseException):
    """Raised when required settings/environment variables are invalid or missing."""
