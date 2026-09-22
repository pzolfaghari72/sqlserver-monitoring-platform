/*
===============================================================================
Table: monitoring.system_health
Purpose:
    Current health state of platform components and monitored SQL Server instances.
Grain:
    One current state row per component.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS monitoring.system_health (
    system_health_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    component_name VARCHAR(100) NOT NULL UNIQUE,
    component_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'unknown',
    host_name VARCHAR(255),
    version VARCHAR(100),
    last_heartbeat_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    last_error_at TIMESTAMPTZ,
    message TEXT,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_system_health_status CHECK(status IN ('unknown','healthy','degraded','unhealthy')),
    CONSTRAINT ck_system_health_failures CHECK(consecutive_failures>=0)
);
CREATE INDEX IF NOT EXISTS ix_system_health_status ON monitoring.system_health(status);
