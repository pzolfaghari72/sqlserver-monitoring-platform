/*
===============================================================================
Table: monitoring.collection_error
Purpose:
    Technical errors generated during collection.
Grain:
    One error record per collection failure.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS monitoring.collection_error (
    collection_error_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    collection_run_key BIGINT NOT NULL REFERENCES monitoring.collection_run(collection_run_key),
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    metric_key BIGINT REFERENCES dimension.dim_metric(metric_key),
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    error_type VARCHAR(100) NOT NULL,
    error_code VARCHAR(100),
    error_message TEXT NOT NULL,
    error_detail TEXT,
    source_component VARCHAR(100),
    source_module VARCHAR(200),
    retry_attempt INTEGER NOT NULL DEFAULT 0,
    is_recoverable BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_collection_error_retry CHECK(retry_attempt>=0),
    CONSTRAINT ck_collection_error_resolved CHECK(resolved_at IS NULL OR resolved_at>=occurred_at)
);
CREATE INDEX IF NOT EXISTS ix_collection_error_run ON monitoring.collection_error(collection_run_key);
CREATE INDEX IF NOT EXISTS ix_collection_error_time ON monitoring.collection_error(occurred_at DESC);
