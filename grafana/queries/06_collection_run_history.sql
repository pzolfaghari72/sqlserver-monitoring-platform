-- Table: collector executions, status, duration, counts, and error totals.
SELECT
    cr.started_at,
    cr.finished_at,
    i.instance_name,
    cr.collection_run_key,
    cr.status,
    cr.duration_seconds,
    cr.metrics_requested,
    cr.metrics_collected,
    cr.records_collected,
    cr.error_count,
    cr.execution_id
FROM monitoring.collection_run AS cr
JOIN dimension.dim_instance AS i ON i.instance_key = cr.instance_key
WHERE $__timeFilter(cr.started_at)
  AND (0 IN (${instance_key:csv}) OR cr.instance_key IN (${instance_key:csv}))
ORDER BY cr.started_at DESC, cr.collection_run_key DESC;
