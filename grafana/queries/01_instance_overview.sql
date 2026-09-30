-- Table: instance availability, last collector run, and latest successful sample.
WITH latest_run AS (
    SELECT DISTINCT ON (cr.instance_key)
        cr.instance_key, cr.collection_run_key, cr.started_at, cr.finished_at,
        cr.status, cr.duration_seconds, cr.error_count, cr.records_collected
    FROM monitoring.collection_run AS cr
    ORDER BY cr.instance_key, cr.started_at DESC, cr.collection_run_key DESC
),
latest_sample AS (
    SELECT x.instance_key, MAX(x.collected_at) AS last_sample_at
    FROM (
        SELECT f.instance_key, f.collected_at
        FROM fact.fact_server_metric AS f WHERE f.status = 'success'
        UNION ALL
        SELECT d.instance_key, f.collected_at
        FROM fact.fact_database_metric AS f
        JOIN dimension.dim_database AS d ON d.database_key = f.database_key
        WHERE f.status = 'success'
    ) AS x
    GROUP BY x.instance_key
)
SELECT
    i.instance_key, s.server_name, i.instance_name, i.environment,
    t.enabled AS target_enabled, t.collection_interval_seconds,
    lr.collection_run_key AS last_collection_run_key, lr.status AS last_run_status,
    lr.started_at AS last_run_started_at, lr.finished_at AS last_run_finished_at,
    lr.duration_seconds AS last_run_duration_seconds, lr.error_count AS last_run_error_count,
    lr.records_collected AS last_run_records_collected, ls.last_sample_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - ls.last_sample_at))::bigint AS sample_age_seconds,
    CASE
        WHEN NOT i.is_active OR NOT s.is_active OR t.enabled IS DISTINCT FROM TRUE THEN 'disabled'
        WHEN ls.last_sample_at IS NULL THEN 'no_data'
        WHEN CURRENT_TIMESTAMP - ls.last_sample_at >
             make_interval(secs => (COALESCE(t.collection_interval_seconds, 60) * 3)::double precision)
            THEN 'stale'
        WHEN lr.status IN ('failed', 'partial') THEN lr.status
        ELSE 'healthy'
    END AS health_state
FROM dimension.dim_instance AS i
JOIN dimension.dim_server AS s ON s.server_key = i.server_key
LEFT JOIN config.monitoring_target AS t ON t.instance_key = i.instance_key
LEFT JOIN latest_run AS lr ON lr.instance_key = i.instance_key
LEFT JOIN latest_sample AS ls ON ls.instance_key = i.instance_key
WHERE (0 IN (${instance_key:csv}) OR i.instance_key IN (${instance_key:csv}))
ORDER BY s.server_name, i.instance_name;
