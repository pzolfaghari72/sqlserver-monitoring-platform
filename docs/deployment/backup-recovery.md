# PostgreSQL Backup and Recovery

## Create a backup

Run from the repository root while PostgreSQL is running:

```bash
make backup
```

The script calls `pg_dump` inside the Compose PostgreSQL container and writes a
timestamped plain SQL file to `backups/`. The directory is intended for local
artifacts and is ignored by Git. Protect dumps as sensitive data: they contain
monitoring configuration, operational history, and potentially query text.

Copy backups off-host to access-controlled storage and define an appropriate
retention policy. A dump on the same host/volume is not protection against
host or disk loss. The command backs up the monitoring PostgreSQL database;
it does not back up SQL Server data or Grafana's volume.

## Restore

There is no repository restore helper. Restore to a PostgreSQL database that is
not serving production traffic. Confirm the target database and take a fresh
backup before replacing any existing data. For the configured Compose
PostgreSQL database, a plain SQL dump can be applied with:

```bash
docker compose exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backups/<dump-file>.sql
```

The command assumes `POSTGRES_USER` and `POSTGRES_DB` are available in the
shell; load them from the trusted `.env` without printing secrets. This restore
into an existing database does not automatically drop conflicting objects and
may fail on duplicate objects/data. For a clean recovery, provision an empty
database/volume deliberately and restore there, or use a reviewed recovery
procedure appropriate to the target. Validate schema objects, recent
collection, API readiness, and Grafana datasource health after restoration.

## Recovery checks

- Confirm the dump is non-empty and can be read by `psql` before relying on it.
- Exercise the restore process periodically in an isolated environment.
- Record the backup timestamp, database version, destination, and validation
	result without recording credentials.
- The backup does not include `.env`; preserve deployment configuration and
	secrets separately using the organization's protected secret/configuration
	management process.

