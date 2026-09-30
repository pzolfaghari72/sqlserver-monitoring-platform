-- Table: failed or canceled SQL Agent job-level outcomes.
SELECT
    COALESCE(j.run_start_at, j.collected_at) AS time,
    i.instance_name,
    j.job_name,
    j.run_id,
    j.run_status,
    j.step_id,
    j.step_name,
    j.step_status,
    j.retry_attempts,
    j.run_duration_seconds,
    j.message,
    j.sqlagent_job_enabled
FROM fact.fact_sqlagent_job AS j
JOIN dimension.dim_instance AS i ON i.instance_key = j.instance_key
WHERE $__timeFilter(COALESCE(j.run_start_at, j.collected_at))
  AND j.run_status IN ('FAILED', 'CANCELED')
  AND j.step_id = 0
  AND (0 IN (${instance_key:csv}) OR j.instance_key IN (${instance_key:csv}))
ORDER BY COALESCE(j.run_start_at, j.collected_at) DESC, j.sqlagent_job_key DESC;
