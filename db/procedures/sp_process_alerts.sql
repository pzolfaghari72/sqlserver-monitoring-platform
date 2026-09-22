/*
===============================================================================
Procedure: monitoring.sp_process_alerts
Purpose:
    Evaluates the current collection run against enabled alert rules, maintains
    active alert lifecycle records and resolves active conditions that were
    explicitly evaluated as clear in the same run.
Grain:
    One active alert condition per rule and scoped target.
===============================================================================
*/

CREATE OR REPLACE PROCEDURE monitoring.sp_process_alerts(p_collection_run_key BIGINT)
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TEMP TABLE tmp_alert_eval ON COMMIT DROP AS
    SELECT
        r.alert_code,
        r.alert_name,
        r.severity,
        r.operator,
        r.threshold_value,
        r.consecutive_occurrences,
        r.cooldown_seconds,
        f.instance_key,
        NULL::BIGINT AS database_key,
        f.metric_key,
        f.collected_at,
        f.metric_value_numeric AS current_value,
        CASE r.operator
            WHEN '>' THEN f.metric_value_numeric > r.threshold_value
            WHEN '>=' THEN f.metric_value_numeric >= r.threshold_value
            WHEN '<' THEN f.metric_value_numeric < r.threshold_value
            WHEN '<=' THEN f.metric_value_numeric <= r.threshold_value
            WHEN '=' THEN f.metric_value_numeric = r.threshold_value
            WHEN '!=' THEN f.metric_value_numeric <> r.threshold_value
        END AS triggered
    FROM fact.fact_server_metric f
    JOIN config.alert_rule r
      ON r.metric_key=f.metric_key
     AND r.enabled
     AND (r.instance_key IS NULL OR r.instance_key=f.instance_key)
     AND r.database_key IS NULL
    WHERE f.collection_run_key=p_collection_run_key
      AND f.status='success'
      AND f.metric_value_numeric IS NOT NULL

    UNION ALL

    SELECT
        r.alert_code,
        r.alert_name,
        r.severity,
        r.operator,
        r.threshold_value,
        r.consecutive_occurrences,
        r.cooldown_seconds,
        d.instance_key,
        f.database_key,
        f.metric_key,
        f.collected_at,
        f.metric_value_numeric,
        CASE r.operator
            WHEN '>' THEN f.metric_value_numeric > r.threshold_value
            WHEN '>=' THEN f.metric_value_numeric >= r.threshold_value
            WHEN '<' THEN f.metric_value_numeric < r.threshold_value
            WHEN '<=' THEN f.metric_value_numeric <= r.threshold_value
            WHEN '=' THEN f.metric_value_numeric = r.threshold_value
            WHEN '!=' THEN f.metric_value_numeric <> r.threshold_value
        END
    FROM fact.fact_database_metric f
    JOIN dimension.dim_database d ON d.database_key=f.database_key
    JOIN config.alert_rule r
      ON r.metric_key=f.metric_key
     AND r.enabled
     AND (r.instance_key IS NULL OR r.instance_key=d.instance_key)
     AND (r.database_key IS NULL OR r.database_key=f.database_key)
    WHERE f.collection_run_key=p_collection_run_key
      AND f.status='success'
      AND f.metric_value_numeric IS NOT NULL;

    INSERT INTO monitoring.alert_event
    (
        instance_key,database_key,metric_key,collection_run_key,alert_code,alert_name,
        severity,status,current_value,threshold_value,message,first_seen_at,last_seen_at,occurrence_count
    )
    SELECT
        e.instance_key,e.database_key,e.metric_key,p_collection_run_key,e.alert_code,e.alert_name,
        e.severity,'open',e.current_value,e.threshold_value,
        format('%s: value %s %s threshold %s',e.alert_name,e.current_value,e.operator,e.threshold_value),
        e.collected_at,e.collected_at,1
    FROM tmp_alert_eval e
    WHERE e.triggered
      AND NOT EXISTS
      (
          SELECT 1 FROM monitoring.alert_event a
          WHERE a.alert_code=e.alert_code
            AND a.instance_key=e.instance_key
            AND a.database_key IS NOT DISTINCT FROM e.database_key
            AND a.status IN ('open','acknowledged')
      )
      AND NOT EXISTS
      (
          SELECT 1 FROM monitoring.alert_event a
          WHERE a.alert_code=e.alert_code
            AND a.instance_key=e.instance_key
            AND a.database_key IS NOT DISTINCT FROM e.database_key
            AND a.resolved_at IS NOT NULL
            AND a.resolved_at > CURRENT_TIMESTAMP - make_interval(secs => e.cooldown_seconds)
      );

    UPDATE monitoring.alert_event a
    SET last_seen_at=e.collected_at,
        current_value=e.current_value,
        threshold_value=e.threshold_value,
        collection_run_key=p_collection_run_key,
        occurrence_count=a.occurrence_count+1,
        updated_at=CURRENT_TIMESTAMP
    FROM tmp_alert_eval e
    WHERE e.triggered
      AND a.alert_code=e.alert_code
      AND a.instance_key=e.instance_key
      AND a.database_key IS NOT DISTINCT FROM e.database_key
      AND a.status IN ('open','acknowledged');

    UPDATE monitoring.alert_event a
    SET status='resolved',
        resolved_at=CURRENT_TIMESTAMP,
        updated_at=CURRENT_TIMESTAMP
    WHERE a.status IN ('open','acknowledged')
      AND NOT EXISTS
      (
          SELECT 1 FROM tmp_alert_eval e
          WHERE e.alert_code=a.alert_code
            AND e.instance_key=a.instance_key
            AND e.database_key IS NOT DISTINCT FROM a.database_key
            AND e.triggered
      )
      AND EXISTS
      (
          SELECT 1 FROM tmp_alert_eval e
          WHERE e.alert_code=a.alert_code
            AND e.instance_key=a.instance_key
            AND e.database_key IS NOT DISTINCT FROM a.database_key
      );
END;
$$;
