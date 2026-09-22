/*
===============================================================================
Seed: dimension.dim_metric
Purpose:
    Canonical metric catalog used by the collector and alert rules.
===============================================================================
*/

INSERT INTO dimension.dim_metric(metric_code,metric_name,category,description,unit,data_type,aggregation_type,warning_threshold,critical_threshold,is_active) VALUES
('CPU_UTILIZATION','CPU Utilization','server','SQL Server process CPU utilization','%','double','avg',80,90,TRUE),
('PAGE_LIFE_EXPECTANCY','Page Life Expectancy','server','Buffer Manager PLE','seconds','double','latest',150,300,TRUE),
('BATCH_REQUESTS_PER_SEC','Batch Requests per Second','server','SQL Server request throughput','requests/sec','double','avg',NULL,NULL,TRUE),
('MEMORY_UTILIZATION','Memory Utilization','server','Physical memory utilization','%','double','latest',80,90,TRUE),
('BLOCKING_SESSION_COUNT','Blocking Sessions','blocking','Current blocked session count','count','double','latest',2,5,TRUE),
('DEADLOCKS_PER_SEC','Deadlocks per Second','deadlock','SQL Server deadlock rate','deadlocks/sec','double','latest',0.1,1,TRUE),
('QUERY_ELAPSED_TIME','Query Elapsed Time','query','Average elapsed time of top queries','ms','double','latest',1000,5000,TRUE),
('DATABASE_SIZE','Database Size','database','Database allocated size','MB','double','latest',NULL,NULL,TRUE),
('LOG_USAGE','Log Space Used','database','Transaction log allocated size in MB','MB','double','latest',NULL,NULL,TRUE),
('BACKUP_AGE_HOURS','Backup Age','backup','Hours since last full backup','hours','double','latest',24,48,TRUE),
('SQL_AGENT_FAILURES','SQL Agent Failures','sql_agent','Failed Agent jobs in the collection window','count','double','sum',1,3,TRUE)
ON CONFLICT(metric_code) DO UPDATE SET metric_name=EXCLUDED.metric_name,category=EXCLUDED.category,description=EXCLUDED.description,unit=EXCLUDED.unit,data_type=EXCLUDED.data_type,aggregation_type=EXCLUDED.aggregation_type,warning_threshold=EXCLUDED.warning_threshold,critical_threshold=EXCLUDED.critical_threshold,is_active=TRUE,updated_at=CURRENT_TIMESTAMP;
