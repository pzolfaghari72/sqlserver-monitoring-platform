/*
===============================================================================
File: 005_create_monitoring_permissions.sql
Purpose:
    Final permission hook for the deployment. The bootstrap database user owns
    all application schemas in the development stack.
Notes:
    Production deployments should replace this with least-privilege grants.
===============================================================================
*/

-- Revoke default public schema access for security hardening
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- ===========================================================================
-- 1. CONFIG SCHEMA
-- ===========================================================================
-- Readers and ETL can read configurations
GRANT USAGE ON SCHEMA config TO monitoring_reader_group, monitoring_collector_group, monitoring_etl_group;
GRANT SELECT ON ALL TABLES IN SCHEMA config TO monitoring_reader_group, monitoring_collector_group, monitoring_etl_group;

-- Only ETL and Admins can alter config
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA config TO monitoring_etl_group;

-- ===========================================================================
-- 2. STAGING SCHEMA (Collector & Airflow Data Ingestion)
-- ===========================================================================
GRANT USAGE ON SCHEMA staging TO monitoring_collector_group, monitoring_etl_group;
GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON ALL TABLES IN SCHEMA staging TO monitoring_collector_group, monitoring_etl_group;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA staging TO monitoring_collector_group, monitoring_etl_group;

-- ===========================================================================
-- 3. DIMENSION & FACT SCHEMAS (Data Warehouse Storage)
-- ===========================================================================
-- App / Reader: Read-Only
GRANT USAGE ON SCHEMA dimension, fact TO monitoring_reader_group, monitoring_collector_group, monitoring_etl_group;
GRANT SELECT ON ALL TABLES IN SCHEMA dimension, fact TO monitoring_reader_group, monitoring_etl_group;

-- ETL: Full manipulation on Dimensions & Facts
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA dimension, fact TO monitoring_etl_group;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA dimension, fact TO monitoring_etl_group;

-- ===========================================================================
-- 4. MONITORING SCHEMA (Logs, Heartbeat, Alert Events)
-- ===========================================================================
GRANT USAGE ON SCHEMA monitoring TO monitoring_reader_group, monitoring_collector_group, monitoring_etl_group;
GRANT SELECT ON ALL TABLES IN SCHEMA monitoring TO monitoring_reader_group;

-- Collector and ETL need write access to log runs, errors, and system health
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA monitoring TO monitoring_collector_group, monitoring_etl_group;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA monitoring TO monitoring_collector_group, monitoring_etl_group;

-- ===========================================================================
-- 5. PROCEDURES & FUNCTIONS EXECUTION
-- ===========================================================================
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO monitoring_etl_group;
GRANT EXECUTE ON ALL PROCEDURES IN SCHEMA public TO monitoring_etl_group;

-- ===========================================================================
-- 6. DEFAULT PRIVILEGES (Ensure newly created tables inherit permissions)
-- ===========================================================================
ALTER DEFAULT PRIVILEGES IN SCHEMA staging GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO monitoring_collector_group, monitoring_etl_group;
ALTER DEFAULT PRIVILEGES IN SCHEMA fact GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO monitoring_etl_group;
ALTER DEFAULT PRIVILEGES IN SCHEMA dimension GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO monitoring_etl_group;
ALTER DEFAULT PRIVILEGES IN SCHEMA monitoring GRANT SELECT, INSERT, UPDATE ON TABLES TO monitoring_collector_group, monitoring_etl_group;
ALTER DEFAULT PRIVILEGES IN SCHEMA fact GRANT SELECT ON TABLES TO monitoring_reader_group;
ALTER DEFAULT PRIVILEGES IN SCHEMA dimension GRANT SELECT ON TABLES TO monitoring_reader_group;
ALTER DEFAULT PRIVILEGES IN SCHEMA monitoring GRANT SELECT ON TABLES TO monitoring_reader_group;