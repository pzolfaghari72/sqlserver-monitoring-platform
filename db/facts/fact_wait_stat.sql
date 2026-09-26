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
    CONSTRAINT ck_fact_wait_values CHECK(
        COALESCE(waiting_tasks_count, 0) >= 0 AND 
        COALESCE(wait_time_ms, 0) >= 0 AND 
        COALESCE(signal_wait_time_ms, 0) >= 0 AND 
        COALESCE(max_wait_time_ms, 0) >= 0 AND 
        COALESCE(resource_wait_time_ms, 0) >= 0
    ),
    CONSTRAINT ck_fact_wait_math CHECK(
        wait_time_ms IS NULL OR 
        signal_wait_time_ms IS NULL OR 
        resource_wait_time_ms IS NULL OR 
        wait_time_ms >= (signal_wait_time_ms + resource_wait_time_ms)
    ),
    CONSTRAINT uq_fact_wait_stat_observation UNIQUE(instance_key, wait_type, collected_at, collection_run_key)
);

CREATE INDEX IF NOT EXISTS ix_fact_wait_instance_type_time 
ON fact.fact_wait_stat(instance_key, wait_type, collected_at DESC)
INCLUDE (wait_time_ms, signal_wait_time_ms, resource_wait_time_ms);

CREATE INDEX IF NOT EXISTS ix_fact_wait_instance_time_heavy 
ON fact.fact_wait_stat(instance_key, collected_at DESC)
INCLUDE (wait_type, wait_time_ms);

CREATE INDEX IF NOT EXISTS ix_fact_wait_date 
ON fact.fact_wait_stat(date_key);

CREATE INDEX IF NOT EXISTS ix_fact_wait_run 
ON fact.fact_wait_stat(collection_run_key);

COMMENT ON TABLE fact.fact_wait_stat IS 'Periodic snapshots or deltas of sys.dm_os_wait_stats.';