/*
===============================================================================
Table: config.monitoring_target
Purpose:
    Operational monitoring configuration for each monitored SQL Server instance.
Grain:
    One row per monitored instance.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS config.monitoring_target (
    monitoring_target_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL UNIQUE REFERENCES dimension.dim_instance(instance_key),
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    collection_interval_seconds INTEGER NOT NULL DEFAULT 60,
    connection_timeout_seconds INTEGER NOT NULL DEFAULT 10,
    command_timeout_seconds INTEGER NOT NULL DEFAULT 30,
    max_retry_count INTEGER NOT NULL DEFAULT 3,
    priority INTEGER NOT NULL DEFAULT 100,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_monitoring_target_interval CHECK(collection_interval_seconds>0),
    CONSTRAINT ck_monitoring_target_connection_timeout CHECK(connection_timeout_seconds>0),
    CONSTRAINT ck_monitoring_target_command_timeout CHECK(command_timeout_seconds>0),
    CONSTRAINT ck_monitoring_target_retry CHECK(max_retry_count>=0),
    CONSTRAINT ck_monitoring_target_priority CHECK(priority>=0)
);
CREATE INDEX IF NOT EXISTS ix_monitoring_target_enabled_priority ON config.monitoring_target(enabled,priority);
COMMENT ON TABLE config.monitoring_target IS 'Operational monitoring configuration; secrets are never stored here.';
