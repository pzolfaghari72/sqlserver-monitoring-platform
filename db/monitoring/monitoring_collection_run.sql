/*
===============================================================================
Table: monitoring.collection_run
Purpose:
    Tracks one collector execution for one SQL Server instance.
Grain:
    One collection execution per instance.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS monitoring.collection_run (
    collection_run_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    started_at TIMESTAMPTZ NOT NULL,
    finished_at TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'running',
    collector_name VARCHAR(100),
    collector_version VARCHAR(50),
    metrics_requested INTEGER DEFAULT 0,
    metrics_collected INTEGER DEFAULT 0,
    records_collected BIGINT DEFAULT 0,
    error_count INTEGER NOT NULL DEFAULT 0,
    duration_seconds DOUBLE PRECISION,
    execution_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_collection_run_status CHECK(status IN ('running','success','partial','failed')),
    CONSTRAINT ck_collection_run_counts CHECK(COALESCE(metrics_requested,0)>=0 AND COALESCE(metrics_collected,0)>=0 AND COALESCE(records_collected,0)>=0 AND error_count>=0),
    CONSTRAINT ck_collection_run_finish CHECK(finished_at IS NULL OR finished_at>=started_at)
);
CREATE INDEX IF NOT EXISTS ix_collection_run_instance_time ON monitoring.collection_run(instance_key,started_at DESC);
CREATE INDEX IF NOT EXISTS ix_collection_run_status_time ON monitoring.collection_run(status,started_at DESC);
COMMENT ON TABLE monitoring.collection_run IS 'Collector execution audit and traceability.';
