-- Table: latest stored wait-stat values by instance and wait type.
-- The schema allows snapshots or deltas; these values are deliberately not converted to rates.
WITH latest AS (
    SELECT DISTINCT ON (w.instance_key, w.wait_type)
        w.instance_key, w.wait_type, w.collected_at, w.waiting_tasks_count,
        w.wait_time_ms, w.signal_wait_time_ms, w.resource_wait_time_ms, w.max_wait_time_ms
    FROM fact.fact_wait_stat AS w
    WHERE w.status = 'success'
    ORDER BY w.instance_key, w.wait_type, w.collected_at DESC, w.wait_stat_key DESC
)
SELECT
    i.instance_name,
    w.wait_type,
    w.collected_at,
    w.waiting_tasks_count,
    w.wait_time_ms,
    w.signal_wait_time_ms,
    w.resource_wait_time_ms,
    w.max_wait_time_ms,
    CASE WHEN w.wait_time_ms > 0
         THEN ROUND(100.0 * w.signal_wait_time_ms / w.wait_time_ms, 2)
    END AS signal_wait_pct_of_total
FROM latest AS w
JOIN dimension.dim_instance AS i ON i.instance_key = w.instance_key
WHERE (0 IN (${instance_key:csv}) OR w.instance_key IN (${instance_key:csv}))
ORDER BY w.wait_time_ms DESC NULLS LAST
LIMIT 50;
