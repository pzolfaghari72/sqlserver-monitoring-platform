-- Table: application and collector component health/heartbeat state.
SELECT
    h.component_name,
    h.component_type,
    h.status,
    h.host_name,
    h.version,
    h.last_heartbeat_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - h.last_heartbeat_at))::bigint AS heartbeat_age_seconds,
    h.last_success_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - h.last_success_at))::bigint AS success_age_seconds,
    h.last_error_at,
    h.consecutive_failures,
    h.message
FROM monitoring.system_health AS h
ORDER BY CASE h.status
             WHEN 'unhealthy' THEN 1
             WHEN 'degraded' THEN 2
             WHEN 'unknown' THEN 3
             ELSE 4
         END,
         h.component_type,
         h.component_name;
