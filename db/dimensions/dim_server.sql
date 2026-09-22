/*
===============================================================================
Table: dimension.dim_server
Purpose:
    Master dimension for physical or virtual hosts running SQL Server.
Grain:
    One row per monitored server.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS dimension.dim_server (
    server_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    server_name VARCHAR(200) NOT NULL,
    host_name VARCHAR(255) NOT NULL,
    ip_address INET,
    environment VARCHAR(50) NOT NULL DEFAULT 'development',
    location VARCHAR(100),
    operating_system VARCHAR(200),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_dim_server_host_name UNIQUE (host_name),
    CONSTRAINT ck_dim_server_environment CHECK (environment IN ('development','test','staging','production'))
);
CREATE INDEX IF NOT EXISTS ix_dim_server_environment ON dimension.dim_server(environment);
CREATE INDEX IF NOT EXISTS ix_dim_server_active ON dimension.dim_server(is_active);
COMMENT ON TABLE dimension.dim_server IS 'SQL Server host dimension.';
