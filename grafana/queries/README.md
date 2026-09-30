# SQL Server monitoring queries

These PostgreSQL queries target the schema in the supplied project snapshot. They are panel-query snippets, not dashboard JSON, and should be copied into Grafana PostgreSQL panels.

## Grafana variables

Create these dashboard variables as Query variables using the matching SQL under `variables/`:

- `instance_key`: multi-value, Include All, Custom all value `0`.
- `database_key`: multi-value, Include All, Custom all value `0`.
- `metric_code`: multi-value, Include All, Custom all value `ALL`.

Set the data source to the PostgreSQL database containing the `dimension`, `config`, `fact`, and `monitoring` schemas. Queries use Grafana PostgreSQL macros such as `$__timeFilter`, `$__timeGroupAlias`, `$__timeFrom`, `$__timeTo`, and the variables above.

## Query catalog

- `01_instance_overview.sql`: collection and metric freshness per SQL Server instance.
- `02_server_metric_timeseries.sql`: server-level CPU, memory, PLE, throughput, and other metric trends.
- `03_database_metric_timeseries.sql`: database-level metric trends.
- `04_latest_server_health.sql`, `05_latest_database_health.sql`: latest successful metric values with active alert state.
- `06_collection_run_history.sql`, `07_collection_run_rate.sql`, `08_collection_errors.sql`: collector reliability and error detail.
- `09_active_alerts.sql`: open and acknowledged alert conditions.
- `10_current_blocking.sql`: latest blocking snapshot per instance.
- `11_deadlock_timeline.sql`: deadlock event counts over time.
- `12_latest_waits.sql`: latest stored wait counters.
- `13_top_queries_by_delta.sql`: query CPU/elapsed/IO deltas between snapshots.
- `14_backup_freshness.sql`, `15_failed_backups.sql`: recovery-point freshness and backup failures.
- `16_sql_agent_failures.sql`: failed SQL Agent job executions.
- `17_target_schedule_status.sql`: collection target configuration and last run.
- `18_server_metric_coverage.sql`, `19_database_metric_coverage.sql`: missing/stale metric coverage.
- `20_component_health.sql`: collector and service heartbeat status.
- `21_staging_queue.sql`: rows remaining in staging by collection run.

See [the schema review](../../postgres_schema_review.md) for database design findings.

## Interpretation notes

- The supplied files describe schema and seed definitions, not live table rows. These queries have not been executed against the user's database.
- `fact_wait_stat` is documented as holding either snapshots or deltas. `12_latest_waits.sql` shows the latest sample regardless of the dashboard time range and reports stored values as-is; do not label them as per-second rates until the collector's write semantics are confirmed.
- `dimension.dim_metric` has warning/critical values but no comparison direction. The queries use active records in `monitoring.alert_event` for alert state instead of guessing whether a metric is high-is-bad or low-is-bad.
- `13_top_queries_by_delta.sql` assumes the query-stat total counters are cumulative snapshots, and ignores counter resets and rows without both query hashes. Confirm the collector behavior before relying on this panel.
- `14_backup_freshness.sql` uses the supplied default 24/48-hour backup-age bands; keep them aligned with configured alert rules.
- The snapshot did not contain the existing `grafana/queries` folder or dashboard provisioning files. This library is a ready-to-copy set; it is not yet wired into provisioned dashboards.
