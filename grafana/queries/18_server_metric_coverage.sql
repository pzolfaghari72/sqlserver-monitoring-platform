-- Table: sample coverage for each active server metric and instance in the dashboard range.
SELECT
    i.instance_name,
    m.metric_code,
    m.metric_name,
    m.unit,
    COUNT(f.server_metric_key) AS sample_count,
    COUNT(f.server_metric_key) FILTER (WHERE f.status <> 'success') AS non_success_samples,
    MAX(f.collected_at) AS latest_sample_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(f.collected_at)))::bigint AS sample_age_seconds
FROM dimension.dim_instance AS i
CROSS JOIN dimension.dim_metric AS m
LEFT JOIN fact.fact_server_metric AS f
  ON f.instance_key = i.instance_key
 AND f.metric_key = m.metric_key
 AND $__timeFilter(f.collected_at)
WHERE i.is_active
  AND m.is_active
  AND m.category = 'server'
  AND (0 IN (${instance_key:csv}) OR i.instance_key IN (${instance_key:csv}))
GROUP BY i.instance_name, m.metric_code, m.metric_name, m.unit
ORDER BY i.instance_name, m.metric_name;
