/*
===============================================================================
Table: config.collection_schedule
Purpose:
    Scheduling configuration consumed by the Airflow collection DAG.
Grain:
    One schedule per monitoring target.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS config.collection_schedule (
    collection_schedule_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    monitoring_target_key BIGINT NOT NULL REFERENCES config.monitoring_target(monitoring_target_key),
    schedule_name VARCHAR(100) NOT NULL,
    schedule_type VARCHAR(30) NOT NULL DEFAULT 'interval',
    interval_seconds INTEGER,
    cron_expression VARCHAR(100),
    timezone VARCHAR(100) NOT NULL DEFAULT 'UTC',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    start_at TIMESTAMPTZ,
    end_at TIMESTAMPTZ,
    priority INTEGER NOT NULL DEFAULT 100,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_collection_schedule_type CHECK(schedule_type IN ('interval','cron')),
    CONSTRAINT ck_collection_schedule_interval CHECK(interval_seconds IS NULL OR interval_seconds>0),
    CONSTRAINT ck_collection_schedule_cron CHECK(cron_expression IS NULL OR LENGTH(TRIM(cron_expression))>0),
    CONSTRAINT ck_collection_schedule_priority CHECK(priority>=0),
    CONSTRAINT ck_collection_schedule_time CHECK(end_at IS NULL OR start_at IS NULL OR end_at>start_at),
    CONSTRAINT ck_collection_schedule_definition CHECK((schedule_type='interval' AND interval_seconds IS NOT NULL AND cron_expression IS NULL) OR (schedule_type='cron' AND cron_expression IS NOT NULL AND interval_seconds IS NULL))
);
CREATE INDEX IF NOT EXISTS ix_collection_schedule_target_enabled ON config.collection_schedule(monitoring_target_key,enabled);
COMMENT ON TABLE config.collection_schedule IS 'Collection scheduling configuration executed by Airflow.';
