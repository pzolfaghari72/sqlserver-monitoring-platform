"""Database backup telemetry collector."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import pyodbc

from collector.core.logging import setup_logger

logger = setup_logger(__name__)

# Reads latest FULL (D) backup for all non-system databases
BACKUP_METRICS_QUERY = """
SELECT
    d.name AS database_name,
    MAX(b.backup_start_date) AS backup_start_at,
    MAX(b.backup_finish_date) AS backup_finish_at,
    MAX(b.backup_size) AS backup_size_bytes,
    MAX(b.compressed_backup_size) AS compressed_backup_size_bytes,
    MAX(b.backup_set_id) AS backup_set_id
FROM sys.databases d WITH (NOLOCK)
LEFT JOIN msdb.dbo.backupset b WITH (NOLOCK)
    ON b.database_name = d.name
    AND b.type = 'D'
WHERE d.database_id > 4 -- Ignore system databases (master, tempdb, model, msdb)
GROUP BY d.name;
"""


def collect_backup_metrics(
    conn: pyodbc.Connection,
    run_key: int,
    instance_key: int,
) -> List[Dict[str, Any]]:
    """Extract latest full backup status and timestamps across user databases."""
    collected_at = datetime.now(timezone.utc)
    results: List[Dict[str, Any]] = []

    with conn.cursor() as cur:
        cur.execute(BACKUP_METRICS_QUERY)
        for row in cur.fetchall():
            db_name = row[0]
            start_at = row[1]
            finish_at = row[2]
            backup_size = row[3]
            compressed_size = row[4]
            backup_set_id = row[5]

            if not start_at:
                continue

            duration_sec = None
            if finish_at and start_at:
                duration_sec = max(0.0, (finish_at - start_at).total_seconds())

            results.append(
                {
                    "collection_run_key": run_key,
                    "instance_key": instance_key,
                    "collected_at": collected_at,
                    "database_name": db_name,
                    "backup_start_at": start_at,
                    "backup_finish_at": finish_at,
                    "backup_type": "FULL",
                    "backup_status": "SUCCESS" if finish_at else "FAILED",
                    "duration_seconds": duration_sec,
                    "backup_size_bytes": int(backup_size or 0),
                    "compressed_backup_size_bytes": int(compressed_size or 0),
                    "backup_set_id": int(backup_set_id) if backup_set_id else None,
                    "physical_device_type": None,
                    "status": "success",
                }
            )

    return results
