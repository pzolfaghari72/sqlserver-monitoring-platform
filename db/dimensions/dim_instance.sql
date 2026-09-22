/*
===============================================================================
Table: dimension.dim_instance
Purpose:
    SQL Server instance master dimension.
Grain:
    One row per SQL Server instance.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS dimension.dim_instance (
    instance_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    server_key BIGINT NOT NULL REFERENCES dimension.dim_server(server_key),
    instance_name VARCHAR(200) NOT NULL,
    instance_version VARCHAR(100),
    edition VARCHAR(100),
    port INTEGER,
    environment VARCHAR(50) NOT NULL DEFAULT 'development',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_dim_instance_server_name UNIQUE(server_key, instance_name),
    CONSTRAINT ck_dim_instance_port CHECK (port IS NULL OR port BETWEEN 1 AND 65535),
    CONSTRAINT ck_dim_instance_environment CHECK (environment IN ('development','test','staging','production'))
);
CREATE INDEX IF NOT EXISTS ix_dim_instance_server ON dimension.dim_instance(server_key);
CREATE INDEX IF NOT EXISTS ix_dim_instance_active ON dimension.dim_instance(is_active);
COMMENT ON TABLE dimension.dim_instance IS 'SQL Server instance dimension.';
