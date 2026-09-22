/*
===============================================================================
Table: monitoring.alert_event
Purpose:
    Stores active and historical threshold alert events.
Grain:
    One active condition per alert code and target.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS monitoring.alert_event (
    alert_event_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    database_key BIGINT REFERENCES dimension.dim_database(database_key),
    metric_key BIGINT REFERENCES dimension.dim_metric(metric_key),
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    alert_code VARCHAR(100) NOT NULL,
    alert_name VARCHAR(200) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'warning',
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    current_value DOUBLE PRECISION,
    threshold_value DOUBLE PRECISION,
    message TEXT NOT NULL,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_alert_event_severity CHECK(severity IN ('info','warning','critical')),
    CONSTRAINT ck_alert_event_status CHECK(status IN ('open','acknowledged','resolved')),
    CONSTRAINT ck_alert_event_occurrences CHECK(occurrence_count>0),
    CONSTRAINT ck_alert_event_times CHECK(last_seen_at>=first_seen_at AND (resolved_at IS NULL OR resolved_at>=first_seen_at))
);
CREATE INDEX IF NOT EXISTS ix_alert_event_active ON monitoring.alert_event(status,last_seen_at DESC);
CREATE INDEX IF NOT EXISTS ix_alert_event_target ON monitoring.alert_event(alert_code,instance_key,status);
COMMENT ON TABLE monitoring.alert_event IS 'Triggered monitoring alert lifecycle records.';
