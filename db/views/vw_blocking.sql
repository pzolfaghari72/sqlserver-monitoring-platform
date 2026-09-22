/*
===============================================================================
View: vw_blocking
Purpose:
    Blocking observations with instance/database context.
Grain:
    One blocked session observation.
===============================================================================
*/

CREATE OR REPLACE VIEW vw_blocking AS
SELECT b.blocking_key,b.collected_at,b.instance_key,i.instance_name,b.database_key,d.database_name,b.blocking_session_id,b.blocked_session_id,b.wait_type,b.wait_time_ms,b.blocking_duration_ms,b.blocking_sql_text,b.blocked_sql_text,b.status
FROM fact.fact_blocking b
JOIN dimension.dim_instance i ON i.instance_key=b.instance_key
LEFT JOIN dimension.dim_database d ON d.database_key=b.database_key;
