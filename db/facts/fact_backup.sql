/*
===============================================================================
Table: fact.fact_backup
Purpose:
    Historical SQL Server backup executions.
Grain:
    One backup execution per database.
===============================================================================
*/

/*
===============================================================================
Table: fact.fact_backup
Purpose:
    Historical SQL Server backup executions and recovery lineage.
Grain:
    One backup execution per database.
Optimization:
    Composite & partial indexes for SLA SLA-gap detection and quick metric lookup.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS fact.fact_backup (
    backup_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    database_key BIGINT NOT NULL REFERENCES dimension.dim_database(database_key),
    date_key INTEGER REFERENCES dimension.dim_date(date_key),
    backup_start_at TIMESTAMPTZ NOT NULL,
    backup_finish_at TIMESTAMPTZ,
    backup_type VARCHAR(20) NOT NULL,
    backup_status VARCHAR(20) NOT NULL,
    duration_seconds DOUBLE PRECISION,
    backup_size_bytes BIGINT,
    compressed_backup_size_bytes BIGINT,
    physical_device_type VARCHAR(30),
    backup_set_id BIGINT,
    media_set_id BIGINT,
    recovery_fork_guid VARCHAR(100),
    is_copy_only BOOLEAN NOT NULL DEFAULT FALSE,
    backup_file_name TEXT,
    error_message TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    collection_run_key BIGINT REFERENCES monitoring.collection_run(collection_run_key),
    CONSTRAINT ck_fact_backup_type CHECK(backup_type IN ('FULL','DIFFERENTIAL','LOG','FILE','FILEGROUP','COPY_ONLY')),
    CONSTRAINT ck_fact_backup_result CHECK(backup_status IN ('SUCCESS','FAILED','CANCELED','UNKNOWN')),
    CONSTRAINT ck_fact_backup_status CHECK(status IN ('success','warning','error')),
    CONSTRAINT ck_fact_backup_timing CHECK(backup_finish_at IS NULL OR backup_finish_at >= backup_start_at)
);

CREATE INDEX IF NOT EXISTS ix_fact_backup_database_time 
ON fact.fact_backup(database_key, backup_start_at DESC);

CREATE INDEX IF NOT EXISTS ix_fact_backup_instance_date 
ON fact.fact_backup(instance_key, date_key);

CREATE INDEX IF NOT EXISTS ix_fact_backup_latest_success 
ON fact.fact_backup(database_key, backup_type, backup_finish_at DESC) 
WHERE backup_status = 'SUCCESS';

CREATE INDEX IF NOT EXISTS ix_fact_backup_run 
ON fact.fact_backup(collection_run_key);

COMMENT ON TABLE fact.fact_backup IS 'Historical SQL Server backup executions and recovery lineage.';
