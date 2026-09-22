/*
===============================================================================
Table: staging.database_metric
Purpose:
    Short-lived landing area for generic database metrics before fact loading.
Grain:
    One raw database metric observation.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS staging.database_metric (
    staging_database_metric_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    collection_run_key BIGINT NOT NULL REFERENCES monitoring.collection_run(collection_run_key),
    database_key BIGINT NOT NULL REFERENCES dimension.dim_database(database_key),
    metric_code VARCHAR(100) NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    metric_value_numeric DOUBLE PRECISION,
    metric_value_text TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    source_record_id VARCHAR(200),
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_staging_database_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT ck_staging_database_value CHECK(metric_value_numeric IS NOT NULL OR metric_value_text IS NOT NULL)
);
CREATE INDEX IF NOT EXISTS ix_staging_database_run ON staging.database_metric(collection_run_key);
