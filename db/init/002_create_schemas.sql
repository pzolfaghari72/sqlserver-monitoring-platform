/*
===============================================================================
File: 002_create_schemas.sql
Purpose:
    Creates all PostgreSQL schemas used by the monitoring platform.
Schemas:
    config, dimension, fact, monitoring, staging, audit
===============================================================================
*/

CREATE SCHEMA IF NOT EXISTS config;
CREATE SCHEMA IF NOT EXISTS dimension;
CREATE SCHEMA IF NOT EXISTS fact;
CREATE SCHEMA IF NOT EXISTS monitoring;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS audit;
