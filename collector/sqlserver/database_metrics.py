"""Database dimensions and storage utilization metrics."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

DATABASE_SYNC_QUERY = """
SELECT
    name,
    database_id,
    recovery_model_desc,
    compatibility_level,
    CASE WHEN database_id <= 4 THEN 1 ELSE 0 END AS is_system_database
FROM sys.databases WITH (NOLOCK);
"""

DATA_FILE_SIZE_QUERY = """
SELECT
    d.name,
    'DATABASE_SIZE' AS metric_code,
    CAST(SUM(CASE WHEN mf.type_desc = 'ROWS' THEN mf.size ELSE 0 END) * 8.0 / 1024.0 AS float) AS size_mb,
    d.state_desc
FROM sys.databases d WITH (NOLOCK)
INNER JOIN sys.master_files mf WITH (NOLOCK)
    ON mf.database_id = d.database_id
GROUP BY d.name, d.state_desc;
"""

LOG_FILE_SIZE_QUERY = """
SELECT
    d.name,
    'LOG_USAGE' AS metric_code,
    CAST(SUM(CASE WHEN mf.type_desc = 'LOG' THEN mf.size ELSE 0 END) * 8.0 / 1024.0 AS float) AS size_mb,
    NULL AS state_desc
FROM sys.databases d WITH (NOLOCK)
INNER JOIN sys.master_files mf WITH (NOLOCK)
    ON mf.database_id = d.database_id
GROUP BY d.name;
"""


def sync_databases(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Synchronize SQL Server database dimension catalog."""
    _ = run_key  # Preserved for contract compatibility
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        cur.execute(DATABASE_SYNC_QUERY)
        for row in cur.fetchall():
            results.append(
                {
                    "instance_key": instance_key,
                    "database_name": row[0],
                    "database_id": int(row[1]),
                    "recovery_model": row[2],
                    "compatibility_level": int(row[3]),
                    "is_system_database": bool(row[4]),
                }
            )

    return results


def collect_database_metrics(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Gather storage space metrics (Rows and Log MB) per database."""
    collected_at = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        for sql_statement in (DATA_FILE_SIZE_QUERY, LOG_FILE_SIZE_QUERY):
            cur.execute(sql_statement)
            for row in cur.fetchall():
                results.append(
                    {
                        "collection_run_key": run_key,
                        "instance_key": instance_key,
                        "database_name": row[0],
                        "metric_code": row[1],
                        "collected_at": collected_at,
                        "metric_value_numeric": float(row[2] or 0.0),
                        "metric_value_text": row[3],
                        "status": "success",
                        "source_record_id": row[0],
                    }
                )

    return results