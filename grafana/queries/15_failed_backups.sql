-- Table: recent failed/canceled backup attempts and their error messages.
SELECT
    b.backup_start_at,
    b.backup_finish_at,
    i.instance_name,
    d.database_name,
    b.backup_type,
    b.backup_status,
    b.status AS collection_status,
    b.duration_seconds,
    b.error_message,
    b.backup_file_name,
    b.collection_run_key
FROM fact.fact_backup AS b
JOIN dimension.dim_instance AS i ON i.instance_key = b.instance_key
JOIN dimension.dim_database AS d ON d.database_key = b.database_key
WHERE $__timeFilter(b.backup_start_at)
  AND (b.backup_status IN ('FAILED', 'CANCELED') OR b.status = 'error')
  AND (0 IN (${instance_key:csv}) OR b.instance_key IN (${instance_key:csv}))
  AND (0 IN (${database_key:csv}) OR b.database_key IN (${database_key:csv}))
ORDER BY b.backup_start_at DESC, b.backup_key DESC;
