/*
===============================================================================
Table: dimension.dim_database
Purpose:
    SQL Server database master dimension.
Grain:
    One row per database within one SQL Server instance.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS dimension.dim_database (
    database_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    instance_key BIGINT NOT NULL REFERENCES dimension.dim_instance(instance_key),
    database_name VARCHAR(256) NOT NULL,
    database_id INTEGER NOT NULL,
    recovery_model VARCHAR(20),
    compatibility_level INTEGER,
    is_system_database BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_dim_database_instance_name UNIQUE(instance_key,database_name),
    CONSTRAINT uq_dim_database_instance_id UNIQUE(instance_key,database_id),
    CONSTRAINT ck_dim_database_id CHECK(database_id >= 1),
    CONSTRAINT ck_dim_database_recovery CHECK(recovery_model IS NULL OR recovery_model IN ('FULL','SIMPLE','BULK_LOGGED'))
);
CREATE INDEX IF NOT EXISTS ix_dim_database_instance ON dimension.dim_database(instance_key);
CREATE INDEX IF NOT EXISTS ix_dim_database_active ON dimension.dim_database(is_active);
COMMENT ON TABLE dimension.dim_database IS 'SQL Server database dimension.';
