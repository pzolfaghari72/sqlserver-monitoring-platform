/*
===============================================================================
File: 004_create_extensions.sql
Purpose:
    Enables only PostgreSQL extensions required by the baseline schema.
Notes:
    The platform uses built-in PostgreSQL functionality only; no extension is required.
===============================================================================
*/

-- Extensions for cryptographic functions and UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Extension for advanced indexing capabilities (composite time-series queries)
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Performance tracking for PostgreSQL self-monitoring (requires shared_preload_libraries in postgresql.conf)
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";