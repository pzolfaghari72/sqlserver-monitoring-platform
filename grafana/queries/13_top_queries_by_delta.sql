-- Table: top queries by counter increases over the selected time range.
-- Assumes total counters are cumulative snapshots; rows after counter resets are ignored.
WITH previous AS (
    SELECT DISTINCT ON (f.instance_key, f.database_key, f.query_hash, f.query_plan_hash)
        f.*
    FROM fact.fact_query_stat AS f
    WHERE f.status = 'success'
      AND f.query_hash IS NOT NULL
      AND f.query_plan_hash IS NOT NULL
      AND f.collected_at < $__timeFrom()::timestamptz
      AND (0 IN (${instance_key:csv}) OR f.instance_key IN (${instance_key:csv}))
      AND (0 IN (${database_key:csv}) OR f.database_key IN (${database_key:csv}))
    ORDER BY f.instance_key, f.database_key, f.query_hash, f.query_plan_hash,
             f.collected_at DESC, f.query_stat_key DESC
),
in_range AS (
    SELECT f.*
    FROM fact.fact_query_stat AS f
    WHERE $__timeFilter(f.collected_at)
      AND f.status = 'success'
      AND f.query_hash IS NOT NULL
      AND f.query_plan_hash IS NOT NULL
      AND (0 IN (${instance_key:csv}) OR f.instance_key IN (${instance_key:csv}))
      AND (0 IN (${database_key:csv}) OR f.database_key IN (${database_key:csv}))
),
samples AS (
    SELECT * FROM previous
    UNION ALL
    SELECT * FROM in_range
),
lagged AS (
    SELECT
        s.*,
        LAG(s.execution_count) OVER q AS previous_execution_count,
        LAG(s.total_cpu_ms) OVER q AS previous_total_cpu_ms,
        LAG(s.total_elapsed_ms) OVER q AS previous_total_elapsed_ms,
        LAG(s.total_logical_reads) OVER q AS previous_total_logical_reads,
        LAG(s.total_logical_writes) OVER q AS previous_total_logical_writes
    FROM samples AS s
    WINDOW q AS (
        PARTITION BY s.instance_key, s.database_key, s.query_hash, s.query_plan_hash
        ORDER BY s.collected_at, s.query_stat_key
    )
),
deltas AS (
    SELECT
        l.*,
        l.execution_count - l.previous_execution_count AS execution_delta,
        l.total_cpu_ms - l.previous_total_cpu_ms AS cpu_delta_ms,
        l.total_elapsed_ms - l.previous_total_elapsed_ms AS elapsed_delta_ms,
        l.total_logical_reads - l.previous_total_logical_reads AS logical_reads_delta,
        l.total_logical_writes - l.previous_total_logical_writes AS logical_writes_delta
    FROM lagged AS l
    WHERE $__timeFilter(l.collected_at)
      AND l.previous_execution_count IS NOT NULL
      AND l.execution_count >= l.previous_execution_count
      AND l.total_cpu_ms IS NOT NULL AND l.previous_total_cpu_ms IS NOT NULL
      AND l.total_cpu_ms >= l.previous_total_cpu_ms
      AND l.total_elapsed_ms IS NOT NULL AND l.previous_total_elapsed_ms IS NOT NULL
      AND l.total_elapsed_ms >= l.previous_total_elapsed_ms
      AND l.total_logical_reads IS NOT NULL AND l.previous_total_logical_reads IS NOT NULL
      AND l.total_logical_reads >= l.previous_total_logical_reads
      AND l.total_logical_writes IS NOT NULL AND l.previous_total_logical_writes IS NOT NULL
      AND l.total_logical_writes >= l.previous_total_logical_writes
)
SELECT
    i.instance_name,
    d.database_name,
    q.query_hash,
    q.query_plan_hash,
    LEFT(MAX(q.query_text), 300) AS query_text_sample,
    SUM(q.execution_delta)::bigint AS executions,
    ROUND((SUM(q.cpu_delta_ms) / 1000.0)::numeric, 2) AS cpu_seconds,
    ROUND((SUM(q.elapsed_delta_ms) / 1000.0)::numeric, 2) AS elapsed_seconds,
    SUM(q.logical_reads_delta)::bigint AS logical_reads,
    SUM(q.logical_writes_delta)::bigint AS logical_writes,
    ROUND((SUM(q.cpu_delta_ms) / NULLIF(SUM(q.execution_delta), 0))::numeric, 2) AS avg_cpu_ms_per_execution,
    ROUND((SUM(q.elapsed_delta_ms) / NULLIF(SUM(q.execution_delta), 0))::numeric, 2) AS avg_elapsed_ms_per_execution
FROM deltas AS q
JOIN dimension.dim_instance AS i ON i.instance_key = q.instance_key
JOIN dimension.dim_database AS d ON d.database_key = q.database_key
GROUP BY i.instance_name, d.database_name, q.query_hash, q.query_plan_hash
ORDER BY SUM(q.cpu_delta_ms) DESC
LIMIT 25;
