-- Table: blockers from the latest successful blocking snapshot per instance.
-- No row may mean no blockers were recorded OR no blocking sample exists; check collection freshness.
WITH latest_snapshot AS (
    SELECT b.instance_key, MAX(b.collected_at) AS collected_at
    FROM fact.fact_blocking AS b
    WHERE b.status = 'success'
    GROUP BY b.instance_key
)
SELECT
    b.collected_at,
    i.instance_name,
    d.database_name,
    b.blocking_session_id,
    b.blocked_session_id,
    b.wait_type,
    b.wait_time_ms,
    b.blocking_duration_ms,
    b.blocked_request_count,
    b.blocking_login_name,
    b.blocked_login_name,
    b.blocking_host_name,
    b.blocked_host_name,
    b.blocking_program_name,
    b.blocked_program_name,
    b.blocking_sql_text,
    b.blocked_sql_text,
    b.resource_description
FROM fact.fact_blocking AS b
JOIN latest_snapshot AS s
  ON s.instance_key = b.instance_key AND s.collected_at = b.collected_at
JOIN dimension.dim_instance AS i ON i.instance_key = b.instance_key
LEFT JOIN dimension.dim_database AS d ON d.database_key = b.database_key
WHERE b.status = 'success'
  AND (0 IN (${instance_key:csv}) OR b.instance_key IN (${instance_key:csv}))
ORDER BY b.blocking_duration_ms DESC NULLS LAST, b.wait_time_ms DESC NULLS LAST;
