-- Table: latest successful full, differential, and log backups per active database.
SELECT
    i.instance_name,
    d.database_name,
    d.recovery_model,
    MAX(b.backup_finish_at) FILTER (
        WHERE b.backup_type = 'FULL'
          AND b.backup_status = 'SUCCESS'
          AND b.status = 'success'
          AND NOT b.is_copy_only
    ) AS last_regular_full_backup_at,
    MAX(b.backup_finish_at) FILTER (
        WHERE b.backup_type = 'DIFFERENTIAL'
          AND b.backup_status = 'SUCCESS'
          AND b.status = 'success'
    ) AS last_differential_backup_at,
    MAX(b.backup_finish_at) FILTER (
        WHERE b.backup_type = 'LOG'
          AND b.backup_status = 'SUCCESS'
          AND b.status = 'success'
    ) AS last_log_backup_at,
    ROUND((
        EXTRACT(EPOCH FROM (
            CURRENT_TIMESTAMP - MAX(b.backup_finish_at) FILTER (
                WHERE b.backup_type = 'FULL'
                  AND b.backup_status = 'SUCCESS'
                  AND b.status = 'success'
                  AND NOT b.is_copy_only
            )
        )) / 3600.0
    )::numeric, 2) AS full_backup_age_hours,
    CASE
        WHEN MAX(b.backup_finish_at) FILTER (
            WHERE b.backup_type = 'FULL'
              AND b.backup_status = 'SUCCESS'
              AND b.status = 'success'
              AND NOT b.is_copy_only
        ) IS NULL THEN 'no_regular_full_backup'
        WHEN CURRENT_TIMESTAMP - MAX(b.backup_finish_at) FILTER (
            WHERE b.backup_type = 'FULL'
              AND b.backup_status = 'SUCCESS'
              AND b.status = 'success'
              AND NOT b.is_copy_only
        ) > INTERVAL '48 hours' THEN 'critical'
        WHEN CURRENT_TIMESTAMP - MAX(b.backup_finish_at) FILTER (
            WHERE b.backup_type = 'FULL'
              AND b.backup_status = 'SUCCESS'
              AND b.status = 'success'
              AND NOT b.is_copy_only
        ) > INTERVAL '24 hours' THEN 'warning'
        ELSE 'ok'
    END AS full_backup_state
FROM dimension.dim_database AS d
JOIN dimension.dim_instance AS i ON i.instance_key = d.instance_key
LEFT JOIN fact.fact_backup AS b ON b.database_key = d.database_key
WHERE d.is_active
  AND (0 IN (${instance_key:csv}) OR d.instance_key IN (${instance_key:csv}))
  AND (0 IN (${database_key:csv}) OR d.database_key IN (${database_key:csv}))
GROUP BY i.instance_name, d.database_name, d.recovery_model
ORDER BY i.instance_name, d.database_name;
