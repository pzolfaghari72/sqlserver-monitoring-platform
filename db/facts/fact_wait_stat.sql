/*
===============================================================================
Table: fact.fact_wait_stat
Purpose:
    Historical wait-stat snapshots.
Grain:
    One wait type per instance and collection timestamp.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS fact.fact_wait_stat (
    wait_stat_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    date_key INTEGER REFERENCES dimension.dim_date(date_key),
    collected_at TIMESTAMPTZ NOT NULL,
    wait_type VARCHAR(120) NOT NULL,
    waiting_tasks_count BIGINT,
    wait_time_ms BIGINT,
    signal_wait_time_ms BIGINT,
    max_wait_time_ms BIGINT,
    resource_wait_time_ms BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    CONSTRAINT ck_fact_wait_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT ck_fact_wait_values CHECK(COALESCE(waiting_tasks_count,0)>=0 AND COALESCE(wait_time_ms,0)>=0 AND COALESCE(signal_wait_time_ms,0)>=0 AND COALESCE(max_wait_time_ms,0)>=0 AND COALESCE(resource_wait_time_ms,0)>=0)
);
CREATE INDEX IF NOT EXISTS ix_fact_wait_instance_time ON fact.fact_wait_stat(instance_key,collected_at DESC);
CREATE INDEX IF NOT EXISTS ix_fact_wait_type_time ON fact.fact_wait_stat(wait_type,collected_at DESC);
