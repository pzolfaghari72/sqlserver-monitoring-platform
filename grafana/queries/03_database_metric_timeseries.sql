-- Time series: numeric database metrics grouped by Grafana interval.
SELECT
    $__timeGroupAlias(f.collected_at, $__interval),
    i.instance_name || ' / ' || d.database_name || ' / ' || m.metric_name AS metric,
    AVG(f.metric_value_numeric)::double precision AS value
FROM fact.fact_database_metric AS f
JOIN dimension.dim_database AS d ON d.database_key = f.database_key
JOIN dimension.dim_instance AS i ON i.instance_key = d.instance_key
JOIN dimension.dim_metric AS m ON m.metric_key = f.metric_key
WHERE $__timeFilter(f.collected_at)
  AND f.status = 'success'
  AND f.metric_value_numeric IS NOT NULL
  AND d.is_active
  AND (0 IN (${instance_key:csv}) OR d.instance_key IN (${instance_key:csv}))
  AND (0 IN (${database_key:csv}) OR f.database_key IN (${database_key:csv}))
  AND ('ALL' IN (${metric_code:sqlstring}) OR m.metric_code IN (${metric_code:sqlstring}))
GROUP BY 1, 2
ORDER BY 1, 2;
