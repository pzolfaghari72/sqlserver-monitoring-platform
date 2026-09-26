/*
===============================================================================
Function: fn_get_metric_value
Purpose:
    Returns the latest successful numeric server metric for an instance at or before a timestamp.
Returns:
    DOUBLE PRECISION or NULL.
===============================================================================
*/

CREATE OR REPLACE FUNCTION monitoring.fn_get_metric_value(
    p_instance_key BIGINT,
    p_metric_key BIGINT,
    p_as_of_time TIMESTAMPTZ DEFAULT clock_timestamp()
)
RETURNS DOUBLE PRECISION
LANGUAGE sql
STABLE
PARALLEL SAFE
SECURITY INVOKER
SET search_path = pg_catalog, fact, dimension, monitoring
AS $$
    SELECT f.metric_value_numeric
    FROM fact.fact_server_metric f
    WHERE f.instance_key = p_instance_key
      AND f.metric_key = p_metric_key
      AND f.collected_at <= COALESCE(p_as_of_time, clock_timestamp())
      AND f.status = 'success'
      AND f.metric_value_numeric IS NOT NULL
    ORDER BY f.collected_at DESC
    LIMIT 1;
$$;

COMMENT ON FUNCTION monitoring.fn_get_metric_value(BIGINT, BIGINT, TIMESTAMPTZ) 
IS 'Returns the latest successful numeric metric value for an instance at or before a given timestamp.';