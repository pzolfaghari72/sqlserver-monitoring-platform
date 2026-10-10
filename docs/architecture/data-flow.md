# Data Flow

## Collection and persistence

1. `sqlserver_collection` polls for enabled targets and selects a due target
	using `config.collection_schedule` (interval or cron, with a timezone for
	cron schedules).
2. The collector creates a `monitoring.collection_run` row and connects to the
	target SQL Server. It synchronizes discovered databases into
	`dimension.dim_database` before writing database-level observations.
3. Generic server and database metrics are written to
	`staging.server_metric` and `staging.database_metric`. Metric codes resolve
	against `dimension.dim_metric` when the load procedures create fact rows.
4. Waits, query statistics, blocking, deadlocks, backups, and SQL Agent job
	history are written to specialized `fact` tables because their grains and
	columns differ from generic metric observations. Derived summaries such as
	blocked-session count, backup age, and SQL Agent failure count use generic
	metric staging.
5. Load procedures transform the run's staging rows into
	`fact.fact_server_metric` and `fact.fact_database_metric`; successful loading
	clears the processed run's staging rows. The daily quality DAG also purges
	staging rows older than three days as a fallback.
6. The collector finalizes the run with a status and counters. Errors are
	recorded in `monitoring.collection_error`.

## Operational state and consumers

The health DAG updates one current `monitoring.system_health` row per target.
The alert DAG finds successful or partial runs that have not been evaluated,
calls `monitoring.sp_process_alerts`, then marks each processed run. Alert
lifecycle records are stored in `monitoring.alert_event`.

Grafana queries the PostgreSQL dimensions, facts, and monitoring tables. The
API exposes selected target and alert operations, and the portal consumes that
API. The API does not expose raw collector ingestion or general SQL access.

Wait statistics and query-stat DMV values have reset/cumulative semantics;
snapshots should not be interpreted as rates without calculating deltas and
accounting for engine restarts or cache resets.
