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

SELECT current_database() AS initialized_database;
