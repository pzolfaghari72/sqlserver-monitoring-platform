# Collected SQL Server Metrics

The collector reads SQL Server DMVs and system catalogs. Availability and
values depend on SQL Server edition/version, permissions, workload, and whether
the relevant feature is enabled. Query modules under `collector/sqlserver/`
are authoritative for query details.

| Domain | Collection behavior | Persistence and interpretation |
|---|---|---|
| Server counters | Reads SQL process CPU utilization from the scheduler monitor ring buffer, page life expectancy, batch requests counter, and host memory utilization. | Generic server metric staging, then `fact.fact_server_metric`. The batch counter is collected as exposed by the DMV; it is not normalized into a per-second delta by this collector. |
| Database size | Sums row-data file sizes per database and captures database state. | Generic database metric fact (`DATABASE_SIZE`), in MB. |
| Log size | Sums log-file sizes per database. | Generic database metric fact (`LOG_USAGE`), in MB; this value is log file size, not percent used. |
| Wait statistics | Captures the top 20 non-excluded wait types by cumulative `wait_time_ms`. | `fact.fact_wait_stat`, including waiting tasks and resource/signal/max wait counters. Values can reset with SQL Server and are snapshots, not rates. |
| Query statistics | Captures up to 20 cached query-stat rows ordered by total worker time, with database/query/plan identifiers and execution totals/averages. | `fact.fact_query_stat`; query text is truncated to 4,000 characters. DMV data is cache-based and can reset or disappear when plans are evicted. |
| Blocking | Captures point-in-time blocked-session details, session context, wait details, and SQL/resource text. | `fact.fact_blocking`; this is a sampled view and can miss short-lived blocking incidents. |
| Deadlocks | Reads `xml_deadlock_report` events from the `system_health` Extended Events ring buffer. | `fact.fact_deadlock`, deduplicated by instance and graph hash. The ring buffer is transient; collection may miss events that roll out before the next poll. |
| Backups | Reads the latest full-backup history for non-system databases from `msdb`. | `fact.fact_backup`; backup age is also emitted as a database metric when a finish time is present. The collector does not inspect backup files or prove restorability. |
| SQL Server Agent | Reads job outcome history for the preceding 24 hours (`step_id = 0`). | `fact.fact_sqlagent_job`; failures are also summarized as a server metric. The collector does not capture each job step's detailed history. |

The active metric catalog is seeded in `db/seeds/001_seed_dim_metric.sql`.
Keep metric codes, units, and aggregation semantics aligned with the collector,
alert rules, Grafana queries, and tests. See the [data dictionary](../database/data-dictionary.md)
for fact grains and persisted columns.

## Permissions and sensitive data

The bundled SQL Server initialization grants `VIEW SERVER STATE`,
`VIEW ANY DATABASE`, `VIEW ANY DEFINITION`, and selected `msdb` permissions for
SQL Agent history. Existing SQL Server installations may require
version-specific grants; verify permissions for each enabled query, including
`msdb` backup history and the `system_health` Extended Events ring buffer. Use
a dedicated monitoring login and validate the least privilege required for
your SQL Server version.

Query text, login names, host names, and deadlock/blocking details may contain
sensitive operational or customer information. Restrict access to PostgreSQL,
Grafana, Airflow logs, and backups accordingly.

