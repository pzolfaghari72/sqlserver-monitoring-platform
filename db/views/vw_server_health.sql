/*
===============================================================================
View: vw_server_health
Purpose:
    Latest successful server metric by instance and metric.
Grain:
    One instance x one metric.
===============================================================================
*/

CREATE OR REPLACE VIEW vw_server_health AS
SELECT DISTINCT ON(f.instance_key,f.metric_key) f.instance_key,i.instance_name,i.environment,f.metric_key,m.metric_code,m.metric_name,m.category,m.unit,f.collected_at,f.metric_value_numeric,f.metric_value_text,m.warning_threshold,m.critical_threshold
FROM fact.fact_server_metric f
JOIN dimension.dim_instance i ON i.instance_key=f.instance_key
JOIN dimension.dim_metric m ON m.metric_key=f.metric_key
WHERE i.is_active AND f.status='success'
ORDER BY f.instance_key,f.metric_key,f.collected_at DESC,f.server_metric_key DESC;
