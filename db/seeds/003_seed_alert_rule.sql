/*
===============================================================================
Seed: config.alert_rule
Purpose:
    Creates the default metric threshold rules.
Notes:
    Alert rules use one threshold per row; severity is the severity emitted by that rule.
===============================================================================
*/

INSERT INTO config.alert_rule(alert_code,alert_name,metric_key,operator,threshold_value,severity,enabled,consecutive_occurrences,cooldown_seconds,description)
SELECT v.alert_code,v.alert_name,m.metric_key,v.operator,v.threshold_value,v.severity,v.enabled,v.consecutive_occurrences,v.cooldown_seconds,v.description
FROM (VALUES
('CPU_HIGH','High CPU utilization','CPU_UTILIZATION','>',90.0,'critical',TRUE,1,900,'CPU utilization above the critical threshold'),
('CPU_WARNING','High CPU utilization warning','CPU_UTILIZATION','>',80.0,'warning',TRUE,1,900,'CPU utilization above the warning threshold'),
('BLOCKING_HIGH','Blocking sessions','BLOCKING_SESSION_COUNT','>',5.0,'critical',TRUE,1,600,'Multiple sessions are blocked'),
('BACKUP_AGE_HIGH','Backup too old','BACKUP_AGE_HOURS','>',48.0,'critical',TRUE,1,1800,'No recent full backup was detected'),
('SQL_AGENT_FAILURE','SQL Agent failures','SQL_AGENT_FAILURES','>',3.0,'critical',TRUE,1,900,'Multiple SQL Agent failures were detected')
) AS v(alert_code,alert_name,metric_code,operator,threshold_value,severity,enabled,consecutive_occurrences,cooldown_seconds,description)
JOIN dimension.dim_metric m ON m.metric_code=v.metric_code
ON CONFLICT(alert_code) DO UPDATE SET alert_name=EXCLUDED.alert_name,metric_key=EXCLUDED.metric_key,operator=EXCLUDED.operator,threshold_value=EXCLUDED.threshold_value,severity=EXCLUDED.severity,enabled=EXCLUDED.enabled,consecutive_occurrences=EXCLUDED.consecutive_occurrences,cooldown_seconds=EXCLUDED.cooldown_seconds,description=EXCLUDED.description,updated_at=CURRENT_TIMESTAMP;
