-- Table: latest successful server metrics with active alert state.
SELECT
    h.instance_key, h.instance_name, h.environment, h.metric_code, h.metric_name,
    h.metric_value_numeric, h.metric_value_text, h.unit, h.collected_at,
    COALESCE(a.active_alert_count, 0) AS active_alert_count,
    COALESCE(a.active_severities, 'ok') AS active_severities
FROM vw_server_health AS h
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS active_alert_count,
           string_agg(DISTINCT e.severity, ', ' ORDER BY e.severity) AS active_severities
    FROM monitoring.alert_event AS e
    WHERE e.instance_key = h.instance_key
      AND e.metric_key = h.metric_key
      AND e.database_key IS NULL
      AND e.status IN ('open', 'acknowledged')
) AS a ON TRUE
WHERE EXISTS (SELECT 1 FROM dimension.dim_metric AS active_metric WHERE active_metric.metric_key = h.metric_key AND active_metric.is_active)
  AND (0 IN (${instance_key:csv}) OR h.instance_key IN (${instance_key:csv}))
  AND ('ALL' IN (${metric_code:sqlstring}) OR h.metric_code IN (${metric_code:sqlstring}))
ORDER BY h.instance_name, h.category, h.metric_name;
