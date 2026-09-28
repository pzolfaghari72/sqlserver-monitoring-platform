/*
===============================================================================
File: 003_create_roles.sql
Purpose:
    Reserved role bootstrap. The development deployment uses one database owner
    account, so no additional login roles are required at initialization.
Notes:
    Production role separation should be implemented by the deployment owner.
===============================================================================
*/

-- 1. Create Base Group Roles (No direct login)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'monitoring_reader_group') THEN
        CREATE ROLE monitoring_reader_group NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'monitoring_collector_group') THEN
        CREATE ROLE monitoring_collector_group NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'monitoring_etl_group') THEN
        CREATE ROLE monitoring_etl_group NOLOGIN;
    END IF;
END
$$;

-- 2. Create Functional Users (Passwords should be overridden via secrets/env in actual deployment)
DO $$
BEGIN
    -- User for Dashboards / Web Application (Read-Only)
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE USER app_user WITH PASSWORD 'app@123456';
        GRANT monitoring_reader_group TO app_user;
    END IF;

    -- User for Collector Engine & Heartbeat Probes
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'collector_user') THEN
        CREATE USER collector_user WITH PASSWORD 'collector@123456';
        GRANT monitoring_collector_group TO collector_user;
    END IF;

    -- User for Airflow Tasks & SP Orchestration
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'etl_user') THEN
        CREATE USER etl_user WITH PASSWORD 'etl@123456';
        GRANT monitoring_etl_group TO etl_user;
    END IF;
END
$$;