/*
===============================================================================
Function: fn_get_metric_value
Purpose:
    Returns the latest successful numeric server metric for an instance at or before a timestamp.
Returns:
    DOUBLE PRECISION or NULL.
===============================================================================
*/

CREATE OR REPLACE FUNCTION monitoring.fn_get_metric_value(p_instance_key BIGINT,p_metric_key BIGINT,p_as_of_time TIMESTAMPTZ)
RETURNS DOUBLE PRECISION
LANGUAGE SQL STABLE
AS $$
    SELECT f.metric_value_numeric
    FROM fact.fact_server_metric f
    WHERE f.instance_key=p_instance_key
      AND f.metric_key=p_metric_key
      AND f.collected_at<=p_as_of_time
      AND f.status='success'
      AND f.metric_value_numeric IS NOT NULL
    ORDER BY f.collected_at DESC,f.server_metric_key DESC
    LIMIT 1;
$$;
COMMENT ON FUNCTION monitoring.fn_get_metric_value(BIGINT,BIGINT,TIMESTAMPTZ) IS 'Returns the latest successful numeric metric value.';
