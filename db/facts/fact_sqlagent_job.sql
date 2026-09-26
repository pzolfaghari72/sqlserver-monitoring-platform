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
    job_id UUID NOT NULL,
    job_name VARCHAR(256) NOT NULL,
    run_id BIGINT,                    
    run_requested_at TIMESTAMPTZ,
    run_start_at TIMESTAMPTZ,
    run_finish_at TIMESTAMPTZ,
    run_duration_seconds DOUBLE PRECISION,   
    run_status VARCHAR(20) NOT NULL,
    retry_attempts INTEGER DEFAULT 0,
    step_id INTEGER NOT NULL DEFAULT 0, 
    step_name VARCHAR(256),
    step_status VARCHAR(20),
    message TEXT,
    sqlagent_job_enabled BOOLEAN,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),

    -- اعتبارسنجی وضعیت‌ها
    CONSTRAINT ck_fact_agent_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT ck_fact_agent_run_status CHECK(run_status IN ('SUCCESS','FAILED','RETRY','CANCELED','UNKNOWN','IN_PROGRESS')),
    CONSTRAINT ck_fact_agent_step_status CHECK(step_status IS NULL OR step_status IN ('SUCCESS','FAILED','RETRY','CANCELED','UNKNOWN')),
    CONSTRAINT ck_fact_agent_step_id CHECK(step_id >= 0),
    CONSTRAINT ck_fact_agent_duration CHECK(duration_seconds IS NULL OR duration_seconds >= 0),
    
    CONSTRAINT uq_fact_sqlagent_job_history UNIQUE(instance_key, run_id)
);

CREATE INDEX IF NOT EXISTS ix_fact_agent_job_time 
ON fact.fact_sqlagent_job(instance_key, run_start_at DESC);

CREATE INDEX IF NOT EXISTS ix_fact_agent_job_lookup 
ON fact.fact_sqlagent_job(instance_key, job_id, run_start_at DESC);

CREATE INDEX IF NOT EXISTS ix_fact_agent_job_failed 
ON fact.fact_sqlagent_job(instance_key, run_start_at DESC) 
WHERE run_status = 'FAILED' AND step_id = 0;

CREATE INDEX IF NOT EXISTS ix_fact_agent_job_date 
ON fact.fact_sqlagent_job(date_key);

CREATE INDEX IF NOT EXISTS ix_fact_agent_job_run 
ON fact.fact_sqlagent_job(collection_run_key);

COMMENT ON TABLE fact.fact_sqlagent_job IS 'Historical SQL Server Agent job executions and step traces.';
