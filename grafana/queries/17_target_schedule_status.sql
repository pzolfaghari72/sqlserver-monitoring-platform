-- Table: active target configuration, selected schedule, and most recent collection run.
SELECT
    s.server_name,
    i.instance_name,
    i.instance_key,
    t.monitoring_target_key,
    t.enabled AS target_enabled,
    t.collection_interval_seconds AS fallback_interval_seconds,
    cs.schedule_name,
    cs.schedule_type,
    cs.interval_seconds,
    cs.cron_expression,
    cs.timezone,
    cs.priority AS schedule_priority,
    lr.started_at AS last_run_started_at,
    lr.finished_at AS last_run_finished_at,
    lr.status AS last_run_status,
    CASE
        WHEN cs.monitoring_target_key IS NULL THEN 'no_active_schedule'
        WHEN cs.schedule_type = 'interval' AND lr.finished_at IS NOT NULL
            THEN lr.finished_at + make_interval(secs => cs.interval_seconds::double precision)
        WHEN cs.schedule_type = 'interval' AND lr.finished_at IS NULL
            THEN COALESCE(lr.started_at, t.created_at) + make_interval(secs => cs.interval_seconds::double precision)
        ELSE NULL
    END AS next_interval_due_at
FROM config.monitoring_target AS t
JOIN dimension.dim_instance AS i ON i.instance_key = t.instance_key
JOIN dimension.dim_server AS s ON s.server_key = i.server_key
LEFT JOIN LATERAL (
    SELECT cs.*
    FROM config.collection_schedule AS cs
    WHERE cs.monitoring_target_key = t.monitoring_target_key
      AND cs.enabled
      AND (cs.start_at IS NULL OR cs.start_at <= CURRENT_TIMESTAMP)
      AND (cs.end_at IS NULL OR cs.end_at > CURRENT_TIMESTAMP)
    ORDER BY cs.priority, cs.collection_schedule_key
    LIMIT 1
) AS cs ON TRUE
LEFT JOIN LATERAL (
    SELECT cr.started_at, cr.finished_at, cr.status
    FROM monitoring.collection_run AS cr
    WHERE cr.instance_key = t.instance_key
    ORDER BY cr.started_at DESC, cr.collection_run_key DESC
    LIMIT 1
) AS lr ON TRUE
WHERE (0 IN (${instance_key:csv}) OR i.instance_key IN (${instance_key:csv}))
ORDER BY t.priority, s.server_name, i.instance_name;
