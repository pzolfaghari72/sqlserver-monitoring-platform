/*
===============================================================================
Table: config.alert_rule
Purpose:
    Threshold rules evaluated by monitoring.sp_process_alerts.
Grain:
    One alert rule.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS config.alert_rule (
    alert_rule_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    alert_code VARCHAR(100) NOT NULL UNIQUE,
    alert_name VARCHAR(200) NOT NULL,
    metric_key BIGINT NOT NULL REFERENCES dimension.dim_metric(metric_key),
    instance_key BIGINT REFERENCES dimension.dim_instance(instance_key),
    database_key BIGINT REFERENCES dimension.dim_database(database_key),
    operator VARCHAR(10) NOT NULL,
    threshold_value DOUBLE PRECISION NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'warning',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    evaluation_window_seconds INTEGER,
    consecutive_occurrences INTEGER NOT NULL DEFAULT 1,
    cooldown_seconds INTEGER NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_alert_rule_operator CHECK(operator IN ('>','>=','<','<=','=','!=')),
    CONSTRAINT ck_alert_rule_severity CHECK(severity IN ('info','warning','critical')),
    CONSTRAINT ck_alert_rule_window CHECK(evaluation_window_seconds IS NULL OR evaluation_window_seconds>0),
    CONSTRAINT ck_alert_rule_occurrences CHECK(consecutive_occurrences>0),
    CONSTRAINT ck_alert_rule_cooldown CHECK(cooldown_seconds>=0)
);
CREATE INDEX IF NOT EXISTS ix_alert_rule_metric_enabled ON config.alert_rule(metric_key,enabled);
COMMENT ON TABLE config.alert_rule IS 'Configurable metric threshold rules.';
