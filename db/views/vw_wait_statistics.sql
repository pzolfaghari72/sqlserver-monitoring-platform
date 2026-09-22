/*
===============================================================================
View: vw_wait_statistics
Purpose:
    Wait statistics with instance context.
Grain:
    One wait type observation.
===============================================================================
*/

CREATE OR REPLACE VIEW vw_wait_statistics AS
SELECT w.wait_stat_key,w.instance_key,i.instance_name,w.collected_at,w.wait_type,w.waiting_tasks_count,w.wait_time_ms,w.signal_wait_time_ms,w.max_wait_time_ms,w.resource_wait_time_ms,w.status,w.collection_run_key
FROM fact.fact_wait_stat w
JOIN dimension.dim_instance i ON i.instance_key=w.instance_key;
