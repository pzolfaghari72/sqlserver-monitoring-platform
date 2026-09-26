/*
===============================================================================
Table: fact.fact_deadlock
Purpose:
    Detected deadlock events.
Grain:
    One distinct deadlock graph per instance.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS fact.fact_deadlock (
    deadlock_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    database_key BIGINT REFERENCES dimension.dim_database(database_key),
    date_key INTEGER REFERENCES dimension.dim_date(date_key),
    occurred_at TIMESTAMPTZ NOT NULL,
    victim_session_id INTEGER,
    transaction_count INTEGER,
    involved_session_count INTEGER,
    deadlock_type VARCHAR(100),
    resource_count INTEGER,
    victim_login_name VARCHAR(256),
    victim_host_name VARCHAR(256),
    victim_program_name VARCHAR(256),
    victim_sql_text TEXT,
    deadlock_graph TEXT, -- در صورت تمایل می‌توان از نوع XML در PostgreSQL استفاده نمود
    deadlock_hash VARCHAR(128) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    CONSTRAINT ck_fact_deadlock_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT uq_fact_deadlock_hash UNIQUE(instance_key, deadlock_hash)
);

CREATE INDEX IF NOT EXISTS ix_fact_deadlock_instance_time 
ON fact.fact_deadlock(instance_key, occurred_at DESC);

CREATE INDEX IF NOT EXISTS ix_fact_deadlock_database_time 
ON fact.fact_deadlock(database_key, occurred_at DESC)
WHERE database_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_fact_deadlock_date 
ON fact.fact_deadlock(date_key);

CREATE INDEX IF NOT EXISTS ix_fact_deadlock_run 
ON fact.fact_deadlock(collection_run_key);

COMMENT ON TABLE fact.fact_deadlock IS 'Detected deadlock events and XML graphs.';