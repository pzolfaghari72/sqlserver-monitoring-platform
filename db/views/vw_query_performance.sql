/*
===============================================================================
View: vw_query_performance
Purpose:
    Query performance snapshots with database and instance context.
Grain:
    One query snapshot.
===============================================================================
*/

CREATE OR REPLACE VIEW vw_query_performance AS
SELECT q.query_stat_key,q.instance_key,i.instance_name,q.database_key,d.database_name,q.collected_at,q.query_hash,q.query_plan_hash,q.execution_count,q.total_elapsed_ms,q.total_cpu_ms,q.total_logical_reads,q.total_logical_writes,q.avg_elapsed_ms,q.avg_cpu_ms,q.avg_logical_reads,q.query_text,q.status,q.collection_run_key
FROM fact.fact_query_stat q
JOIN dimension.dim_instance i ON i.instance_key=q.instance_key
JOIN dimension.dim_database d ON d.database_key=q.database_key;
