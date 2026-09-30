-- Table: sample coverage for each active database metric and active database in the range.
SELECT
    i.instance_name,
    d.database_name,
    m.metric_code,
    m.metric_name,
    m.unit,
    COUNT(f.database_metric_key) AS sample_count,
    COUNT(f.database_metric_key) FILTER (WHERE f.status <> 'success') AS non_success_samples,
    MAX(f.collected_at) AS latest_sample_at,
    EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - MAX(f.collected_at)))::bigint AS sample_age_seconds
FROM dimension.dim_database AS d
JOIN dimension.dim_instance AS i ON i.instance_key = d.instance_key
CROSS JOIN dimension.dim_metric AS m
LEFT JOIN fact.fact_database_metric AS f
  ON f.database_key = d.database_key
 AND f.metric_key = m.metric_key
 AND $__timeFilter(f.collected_at)
WHERE d.is_active
  AND i.is_active
  AND m.is_active
  AND m.category = 'database'
  AND (0 IN (${instance_key:csv}) OR d.instance_key IN (${instance_key:csv}))
  AND (0 IN (${database_key:csv}) OR d.database_key IN (${database_key:csv}))
GROUP BY i.instance_name, d.database_name, m.metric_code, m.metric_name, m.unit
ORDER BY i.instance_name, d.database_name, m.metric_name;
