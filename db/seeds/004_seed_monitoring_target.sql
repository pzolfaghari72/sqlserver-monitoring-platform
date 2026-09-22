/*
===============================================================================
Seed: dimension.dim_server / dimension.dim_instance / config.monitoring_target
Purpose:
    Creates or updates the development monitoring target from deployment variables.
Parameters:
    server_name, server_ip, environment, instance_name, server_port.
===============================================================================
*/

INSERT INTO dimension.dim_server(server_name,host_name,ip_address,environment,operating_system)
VALUES(:'server_name',:'server_name',NULL,:'environment','SQL Server monitored host')
ON CONFLICT(host_name) DO UPDATE SET server_name=EXCLUDED.server_name,environment=EXCLUDED.environment,is_active=TRUE,updated_at=CURRENT_TIMESTAMP;
INSERT INTO dimension.dim_instance(server_key,instance_name,port,environment,is_active)
SELECT server_key,:'instance_name',:'server_port'::int,:'environment',TRUE FROM dimension.dim_server WHERE host_name=:'server_name'
ON CONFLICT(server_key,instance_name) DO UPDATE SET port=EXCLUDED.port,environment=EXCLUDED.environment,is_active=TRUE,updated_at=CURRENT_TIMESTAMP;
INSERT INTO config.monitoring_target(instance_key,enabled,collection_interval_seconds,connection_timeout_seconds,command_timeout_seconds,max_retry_count,priority,description)
SELECT instance_key,TRUE,60,15,60,3,100,'Default development monitoring target' FROM dimension.dim_instance i JOIN dimension.dim_server s ON s.server_key=i.server_key WHERE s.host_name=:'server_name' AND i.instance_name=:'instance_name'
ON CONFLICT(instance_key) DO UPDATE SET enabled=TRUE,updated_at=CURRENT_TIMESTAMP;
INSERT INTO config.collection_schedule(monitoring_target_key,schedule_name,schedule_type,interval_seconds,timezone,enabled,priority,description)
SELECT monitoring_target_key,'Default collection','interval',60,'UTC',TRUE,100,'One-minute Airflow polling schedule' FROM config.monitoring_target t JOIN dimension.dim_instance i ON i.instance_key=t.instance_key JOIN dimension.dim_server s ON s.server_key=i.server_key WHERE s.host_name=:'server_name' AND i.instance_name=:'instance_name'
AND NOT EXISTS(SELECT 1 FROM config.collection_schedule cs WHERE cs.monitoring_target_key=t.monitoring_target_key AND cs.schedule_name='Default collection');
