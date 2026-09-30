-- Time series: number of recorded deadlock events.
SELECT
    $__timeGroupAlias(d.occurred_at, $__interval),
    i.instance_name AS metric,
    COUNT(*)::double precision AS value
FROM fact.fact_deadlock AS d
JOIN dimension.dim_instance AS i ON i.instance_key = d.instance_key
WHERE $__timeFilter(d.occurred_at)
  AND d.status = 'success'
  AND (0 IN (${instance_key:csv}) OR d.instance_key IN (${instance_key:csv}))
GROUP BY 1, 2
ORDER BY 1, 2;
