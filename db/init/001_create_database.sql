/*
===============================================================================
File: 001_create_database.sql
Purpose:
    Documents database creation. Docker Compose creates the application database
    before this initialization layer runs; this script is intentionally a no-op.
Notes:
    The script is kept so manual bootstrap and the project execution order are explicit.
===============================================================================
*/

SELECT 'CREATE DATABASE sqlserver_monitoring'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sqlserver_monitoring')\gexec
