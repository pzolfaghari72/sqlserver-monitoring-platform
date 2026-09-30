-- Table: current alert lifecycle records. Resolved alerts are excluded.
SELECT
    e.severity,
    e.status,
    e.alert_code,
    e.alert_name,
    i.instance_name,
    d.database_name,
    m.metric_code,
    e.current_value,
    e.threshold_value,
    e.message,
    e.first_seen_at,
    e.last_seen_at,
    e.occurrence_count,
    e.collection_run_key
FROM monitoring.alert_event AS e
JOIN dimension.dim_instance AS i ON i.instance_key = e.instance_key
LEFT JOIN dimension.dim_database AS d ON d.database_key = e.database_key
LEFT JOIN dimension.dim_metric AS m ON m.metric_key = e.metric_key
WHERE e.status IN ('open', 'acknowledged')
  AND (0 IN (${instance_key:csv}) OR e.instance_key IN (${instance_key:csv}))
  AND (0 IN (${database_key:csv}) OR e.database_key IS NULL OR e.database_key IN (${database_key:csv}))
ORDER BY CASE e.severity WHEN 'critical' THEN 1 WHEN 'warning' THEN 2 ELSE 3 END,
         e.last_seen_at DESC;
