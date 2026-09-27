/*
===============================================================================
Function: config.trg_set_updated_at
Purpose:
    Shared BEFORE UPDATE trigger function that stamps updated_at with the
    current time on any row change.
Used by:
    dimension.dim_server, dimension.dim_instance, dimension.dim_database,
    dimension.dim_metric -- each attaches its own trg_<table>_updated_at
    trigger to this one shared function rather than defining its own copy.
Notes:
    Originally defined inline inside db/dimensions/dim_server.sql and only
    usable by the other dimension files because dim_server.sql happened to
    run first in scripts/bootstrap/init_database.sh. Moved here so the
    dependency is explicit: this file is now run directly by
    init_database.sh immediately after db/init/004_create_extensions.sql,
    before any dimension table is created.
===============================================================================
*/
CREATE OR REPLACE FUNCTION config.trg_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
 