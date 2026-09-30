-- Table: technical collector errors within the dashboard time range.
SELECT
    e.occurred_at,
    i.instance_name,
    m.metric_code,
    e.error_type,
    e.error_code,
    e.error_message,
    e.error_detail,
    e.source_component,
    e.source_module,
    e.retry_attempt,
    e.is_recoverable,
    e.resolved_at,
    e.collection_run_key
FROM monitoring.collection_error AS e
JOIN dimension.dim_instance AS i ON i.instance_key = e.instance_key
LEFT JOIN dimension.dim_metric AS m ON m.metric_key = e.metric_key
WHERE $__timeFilter(e.occurred_at)
  AND (0 IN (${instance_key:csv}) OR e.instance_key IN (${instance_key:csv}))
ORDER BY e.occurred_at DESC, e.collection_error_key DESC;
