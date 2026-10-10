# Collector Design

The collector package separates SQL Server extraction, PostgreSQL persistence,
configuration, and orchestration:

- `collector/sqlserver/` contains one query/transform module per telemetry
	domain, plus SQL Server connection handling.
- `collector/services/monitoring.py` coordinates the collection pipeline.
- `collector/repository/postgres.py` writes runs, dimensions, staging rows,
	specialized facts, errors, and load-procedure calls.
- `collector/core/config.py` validates environment configuration with Pydantic
	Settings; password fields use `SecretStr`.
- `collector/collector.py` provides a standalone polling entry point. The
	Compose stack instead invokes the monitoring service from Airflow tasks.

## Run lifecycle

For each target the service creates a `monitoring.collection_run`, opens a
SQL Server connection, synchronizes discovered databases, and runs the
registered collectors. Server/database metrics pass through staging;
waits, blocking, deadlocks, query stats, backups, and SQL Agent records use
specialized persistence. Derived summaries for blocked sessions, backup age,
and SQL Agent failures are staged as generic metrics. The service executes the
staging load procedures, records collector errors, and finalizes run counters
and status.

Each collector is isolated so one domain's failure can be logged without
necessarily discarding successfully gathered domains. Check both the overall
run status and `monitoring.collection_error` before treating a partial run as
complete. Fatal connection or persistence failures can prevent the normal load
path; inspect staging for orphaned work, which is eventually removed by the
three-day staging purge.

## Configuration and extension points

The collector requires SQL Server host, user, and password plus PostgreSQL
host, database, user, and password. Defaults and validation are in
`collector/core/config.py`; Compose supplies deployment-specific values through
`.env`. Airflow replaces target host, port, timeout, and instance key for each
mapped task.

When adding a collector, define its source query and result shape, register it
in `MonitoringService.COLLECTORS`, implement repository persistence for its
grain, ensure all metric codes exist in the metric seed when using generic
staging, and update the data dictionary/dashboard/tests as applicable. Keep
database identifiers and metric codes consistent across those boundaries.

