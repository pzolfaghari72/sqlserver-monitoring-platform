/*
===============================================================================
Procedure: monitoring.sp_load_database_metrics
Purpose:
    Loads staged database metrics into fact.fact_database_metric and clears the processed staging rows.
===============================================================================
*/

CREATE OR REPLACE PROCEDURE monitoring.sp_load_database_metrics(p_collection_run_key BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS(SELECT 1 FROM monitoring.collection_run WHERE collection_run_key=p_collection_run_key) THEN
        RAISE EXCEPTION 'Collection run % does not exist',p_collection_run_key;
    END IF;
    INSERT INTO fact.fact_database_metric(database_key,metric_key,date_key,collected_at,metric_value_numeric,metric_value_text,status,collection_run_key)
    SELECT s.database_key,m.metric_key,TO_CHAR(s.collected_at AT TIME ZONE 'UTC','YYYYMMDD')::int,s.collected_at,s.metric_value_numeric,s.metric_value_text,s.status,s.collection_run_key
    FROM staging.database_metric s
    JOIN dimension.dim_metric m ON m.metric_code=s.metric_code AND m.is_active
    WHERE s.collection_run_key=p_collection_run_key
      AND (s.metric_value_numeric IS NOT NULL OR s.metric_value_text IS NOT NULL)
    ON CONFLICT (database_key,metric_key,collected_at,collection_run_key) DO NOTHING;
    DELETE FROM staging.database_metric WHERE collection_run_key=p_collection_run_key;
END;
$$;
