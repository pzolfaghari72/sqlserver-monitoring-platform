/*
===============================================================================
Table: fact.fact_query_stat
Purpose:
    Historical top-query performance snapshots.
Grain:
    One query snapshot per database and collection timestamp.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS fact.fact_query_stat (
    query_stat_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    database_key BIGINT NOT NULL REFERENCES dimension.dim_database(database_key),
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    date_key INTEGER REFERENCES dimension.dim_date(date_key),
    collected_at TIMESTAMPTZ NOT NULL,
    query_hash BIGINT,
    query_plan_hash BIGINT,
    sql_handle VARCHAR(128),
    plan_handle VARCHAR(128),
    query_text TEXT,
    execution_count BIGINT,
    total_elapsed_ms DOUBLE PRECISION,
    total_cpu_ms DOUBLE PRECISION,
    total_logical_reads BIGINT,
    total_logical_writes BIGINT,
    total_physical_reads BIGINT,
    last_elapsed_ms DOUBLE PRECISION,
    last_cpu_ms DOUBLE PRECISION,
    last_logical_reads BIGINT,
    last_logical_writes BIGINT,
    min_elapsed_ms DOUBLE PRECISION,
    max_elapsed_ms DOUBLE PRECISION,
    avg_elapsed_ms DOUBLE PRECISION,
    avg_cpu_ms DOUBLE PRECISION,
    avg_logical_reads DOUBLE PRECISION,
    row_count BIGINT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    CONSTRAINT ck_fact_query_status CHECK(status IN ('success','warning','error'))
);
CREATE INDEX IF NOT EXISTS ix_fact_query_database_time ON fact.fact_query_stat(database_key,collected_at DESC);
CREATE INDEX IF NOT EXISTS ix_fact_query_hash_time ON fact.fact_query_stat(query_hash,collected_at DESC);
