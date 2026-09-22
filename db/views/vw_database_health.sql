/*
===============================================================================
View: vw_database_health
Purpose:
    Latest successful database metric by database and metric.
Grain:
    One database x one metric.
===============================================================================
*/

CREATE OR REPLACE VIEW vw_database_health AS
SELECT DISTINCT ON(f.database_key,f.metric_key) f.database_key,d.database_name,d.instance_key,i.instance_name,f.metric_key,m.metric_code,m.metric_name,m.unit,f.collected_at,f.metric_value_numeric,f.metric_value_text,m.warning_threshold,m.critical_threshold
FROM fact.fact_database_metric f
JOIN dimension.dim_database d ON d.database_key=f.database_key
JOIN dimension.dim_instance i ON i.instance_key=d.instance_key
JOIN dimension.dim_metric m ON m.metric_key=f.metric_key
WHERE d.is_active AND f.status='success'
ORDER BY f.database_key,f.metric_key,f.collected_at DESC,f.database_metric_key DESC;
