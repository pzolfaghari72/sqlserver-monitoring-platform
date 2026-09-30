-- Table: current rows retained in staging, grouped by collection run.
-- If staging is intentionally retained, treat this as staged volume rather than a processing backlog.
WITH staged AS (
    SELECT
        s.collection_run_key,
        s.instance_key,
        s.loaded_at,
        s.collected_at,
        s.status,
        'server'::text AS metric_scope
    FROM staging.server_metric AS s
    UNION ALL
    SELECT
        s.collection_run_key,
        d.instance_key,
        s.loaded_at,
        s.collected_at,
        s.status,
        'database'::text AS metric_scope
    FROM staging.database_metric AS s
    JOIN dimension.dim_database AS d ON d.database_key = s.database_key
)
SELECT
    i.instance_name,
    s.collection_run_key,
    cr.status AS run_status,
    cr.started_at AS run_started_at,
    COUNT(*) AS staged_rows,
    COUNT(*) FILTER (WHERE s.metric_scope = 'server') AS server_metric_rows,
    COUNT(*) FILTER (WHERE s.metric_scope = 'database') AS database_metric_rows,
    COUNT(*) FILTER (WHERE s.status <> 'success') AS non_success_rows,
    MIN(s.loaded_at) AS oldest_loaded_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MIN(s.loaded_at)))::bigint AS oldest_row_age_seconds,
    MAX(s.collected_at) AS latest_sample_at
FROM staged AS s
JOIN dimension.dim_instance AS i ON i.instance_key = s.instance_key
LEFT JOIN monitoring.collection_run AS cr ON cr.collection_run_key = s.collection_run_key
GROUP BY i.instance_name, s.collection_run_key, cr.status, cr.started_at
ORDER BY MIN(s.loaded_at) ASC;
