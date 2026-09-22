/*
===============================================================================
Table: fact.fact_blocking
Purpose:
    Point-in-time blocking observations.
Grain:
    One blocked session per collection timestamp.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS fact.fact_blocking (
    blocking_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    database_key BIGINT REFERENCES dimension.dim_database(database_key),
    date_key INTEGER REFERENCES dimension.dim_date(date_key),
    collected_at TIMESTAMPTZ NOT NULL,
    blocking_session_id INTEGER,
    blocked_session_id INTEGER NOT NULL,
    blocking_status VARCHAR(30),
    wait_type VARCHAR(120),
    wait_time_ms BIGINT,
    blocking_duration_ms BIGINT,
    blocked_request_count INTEGER,
    blocking_login_name VARCHAR(256),
    blocked_login_name VARCHAR(256),
    blocking_host_name VARCHAR(256),
    blocked_host_name VARCHAR(256),
    blocking_program_name VARCHAR(256),
    blocked_program_name VARCHAR(256),
    blocking_sql_text TEXT,
    blocked_sql_text TEXT,
    resource_description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    CONSTRAINT ck_fact_blocking_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT ck_fact_blocking_session CHECK(blocked_session_id>0)
);
CREATE INDEX IF NOT EXISTS ix_fact_blocking_instance_time ON fact.fact_blocking(instance_key,collected_at DESC);
CREATE INDEX IF NOT EXISTS ix_fact_blocking_database_time ON fact.fact_blocking(database_key,collected_at DESC);
