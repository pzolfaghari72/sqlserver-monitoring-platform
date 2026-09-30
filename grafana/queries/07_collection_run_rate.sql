-- Time series: successful, partial, failed, and running collector executions by instance.
SELECT
    $__timeGroupAlias(cr.started_at, $__interval),
    i.instance_name || ' / ' || cr.status AS metric,
    COUNT(*)::double precision AS value
FROM monitoring.collection_run AS cr
JOIN dimension.dim_instance AS i ON i.instance_key = cr.instance_key
WHERE $__timeFilter(cr.started_at)
  AND (0 IN (${instance_key:csv}) OR cr.instance_key IN (${instance_key:csv}))
GROUP BY 1, 2
ORDER BY 1, 2;
