/*
===============================================================================
Table: fact.fact_sqlagent_job
Purpose:
    Historical SQL Server Agent job executions.
Grain:
    One job execution record.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS fact.fact_sqlagent_job (
    sqlagent_job_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    date_key INTEGER REFERENCES dimension.dim_date(date_key),
    collected_at TIMESTAMPTZ NOT NULL,
    job_id UUID,
    job_name VARCHAR(256) NOT NULL,
    run_id BIGINT,
    run_requested_at TIMESTAMPTZ,
    run_start_at TIMESTAMPTZ,
    run_finish_at TIMESTAMPTZ,
    run_duration_seconds DOUBLE PRECISION,
    run_status VARCHAR(20) NOT NULL,
    retry_attempts INTEGER,
    step_id INTEGER,
    step_name VARCHAR(256),
    step_status VARCHAR(20),
    message TEXT,
    sqlagent_job_enabled BOOLEAN,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    CONSTRAINT ck_fact_agent_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT ck_fact_agent_run_status CHECK(run_status IN ('SUCCESS','FAILED','RETRY','CANCELED','UNKNOWN'))
);
CREATE INDEX IF NOT EXISTS ix_fact_agent_job_time ON fact.fact_sqlagent_job(instance_key,run_start_at DESC);
