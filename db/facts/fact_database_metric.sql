/*
===============================================================================
Table: fact.fact_database_metric
Purpose:
    Historical database metric observations.
Grain:
    One metric observation per database and collection timestamp.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS fact.fact_database_metric (
    database_metric_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    database_key BIGINT NOT NULL REFERENCES dimension.dim_database(database_key),
    metric_key BIGINT NOT NULL REFERENCES dimension.dim_metric(metric_key),
    date_key INTEGER REFERENCES dimension.dim_date(date_key),
    collected_at TIMESTAMPTZ NOT NULL,
    metric_value_numeric DOUBLE PRECISION,
    metric_value_text TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    CONSTRAINT ck_fact_database_metric_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT ck_fact_database_metric_value CHECK(metric_value_numeric IS NOT NULL OR metric_value_text IS NOT NULL),
    CONSTRAINT uq_fact_database_metric_observation UNIQUE(database_key,metric_key,collected_at,collection_run_key)
);
CREATE INDEX IF NOT EXISTS ix_fact_database_metric_database_time ON fact.fact_database_metric(database_key,collected_at DESC);
CREATE INDEX IF NOT EXISTS ix_fact_database_metric_metric_time ON fact.fact_database_metric(metric_key,collected_at DESC);
