# Data Dictionary

This page describes the PostgreSQL objects initialized from `db/`. SQL files are
the authoritative source for exact types, defaults, constraints, and indexes.
Generated identity keys are surrogate keys unless noted otherwise. Timestamps
are stored as `TIMESTAMPTZ`; the collector records UTC timestamps.

## Schemas

| Schema | Purpose |
|---|---|
| `dimension` | Stable server, instance, database, metric, and calendar identities. |
| `fact` | Historical time-series observations and SQL Server operational events. |
| `staging` | Temporary landing tables for generic server/database metrics. |
| `monitoring` | Collection audit, errors, alerts, and current health state. |
| `config` | Targets, collection schedules, and threshold rules. |

## Dimensions

### `dimension.dim_server`

**Grain:** One row per host. **Key:** `server_key`.

`server_name` is a display name; `host_name` is the unique connection host;
`ip_address`, `location`, and `operating_system` are optional host metadata.
`environment` is one of `development`, `test`, `staging`, or `production`.
`is_active` controls whether the server is monitored. `created_at` and
`updated_at` record row lifecycle.

### `dimension.dim_instance`

**Grain:** One SQL Server instance on a server. **Key:** `instance_key`.

`server_key` references `dim_server`. `instance_name`, `instance_version`,
`edition`, and `port` describe the SQL Server instance. `environment` and
`is_active` control classification and collection eligibility. Lifecycle
timestamps are `created_at` and `updated_at`.

### `dimension.dim_database`

**Grain:** One database in one instance. **Key:** `database_key`.

`instance_key` references `dim_instance`; `database_name` and `database_id`
identify the source database. `recovery_model`, `compatibility_level`, and
`is_system_database` are synchronized from SQL Server. `is_active` indicates
whether the database is currently present/active. Lifecycle timestamps are
`created_at` and `updated_at`.

### `dimension.dim_metric`

**Grain:** One canonical metric definition. **Key:** `metric_key`; natural key:
`metric_code`.

`metric_name`, `category`, `description`, and `unit` describe the measurement.
`data_type` and `aggregation_type` describe its value and aggregation semantics.
`warning_threshold` and `critical_threshold` are optional catalog metadata;
active alert rules are stored separately in `config.alert_rule`. `is_active`
controls whether the metric is in use. Collection cadence belongs to target
configuration, not this table. Lifecycle timestamps are `created_at` and
`updated_at`.

### `dimension.dim_date`

**Grain:** One calendar date. **Key:** `date_key`, encoded as `YYYYMMDD`;
`full_date` is also unique.

Calendar attributes are `year_number`, `quarter_number`, `month_number`,
`month_name`, `week_of_year`, `day_of_month`, `day_of_year`, `day_of_week`,
`day_name`, and `is_weekend`. Fact `date_key` references are optional; the
timestamp columns remain the precise time source.

## Staging tables

### `staging.server_metric`

**Grain:** One generic server/instance metric observation awaiting fact load.

`staging_server_metric_key` is the row key. `collection_run_key` and
`instance_key` identify its collection and instance; `metric_code` resolves to
`dim_metric.metric_code`. `collected_at`, `metric_value_numeric`,
`metric_value_text`, and `status` hold the observation. `source_record_id` is an
optional source identifier; `loaded_at` is the staging insertion time and drives
the automated staging purge.

### `staging.database_metric`

**Grain:** One generic database metric observation awaiting fact load.

`staging_database_metric_key` is the row key. `collection_run_key` and
`database_key` identify its collection and database; `metric_code` resolves to
`dim_metric.metric_code`. `collected_at`, `metric_value_numeric`,
`metric_value_text`, and `status` hold the observation. `source_record_id` is
optional source context; `loaded_at` is the staging insertion time.

## Fact tables

All fact tables are append-oriented history. Where present, `date_key` is a
calendar lookup and `collection_run_key` links a row to its collection audit
record. The `status` field describes collection of that observation (`success`,
`warning`, or `error`), not the business outcome stored in a specialized fact.

### `fact.fact_server_metric`

**Grain:** One metric observation for an instance, metric, timestamp, and run.

`server_metric_key` is the row key. `instance_key`, `metric_key`, optional
`date_key`, and `collection_run_key` are references. `collected_at` is the
observation time; `metric_value_numeric` and `metric_value_text` hold the
value; `status` records collection state.

### `fact.fact_database_metric`

**Grain:** One metric observation for a database, metric, timestamp, and run.

`database_metric_key` is the row key. `database_key`, `metric_key`, optional
`date_key`, and `collection_run_key` are references. `collected_at`, numeric or
text metric value, and collection `status` have the same meanings as the server
metric fact.

### `fact.fact_wait_stat`

**Grain:** One wait type per instance and collection timestamp.

`wait_stat_key` is the row key. `instance_key`, optional `date_key`, and
`collection_run_key` identify the instance, date, and run. `collected_at` and
`wait_type` identify the snapshot. `waiting_tasks_count`, `wait_time_ms`,
`signal_wait_time_ms`, `max_wait_time_ms`, and `resource_wait_time_ms` contain
the DMV counters; `status` records collection state. Counters are snapshots of
SQL Server cumulative DMV values, not inherently per-interval rates.

### `fact.fact_query_stat`

**Grain:** One captured query-stat row for a database and collection timestamp.

`query_stat_key` is the row key. `database_key`, `instance_key`, optional
`date_key`, and `collection_run_key` identify its context. `collected_at` is the
snapshot time. `query_hash`, `query_plan_hash`, `sql_handle`, and `plan_handle`
identify cached query/plan records; `query_text` stores captured statement
text. `execution_count`, `row_count`, `total_elapsed_ms`, `total_cpu_ms`,
`total_logical_reads`, `total_logical_writes`, and `total_physical_reads` are
cumulative/query totals. `last_elapsed_ms`, `last_cpu_ms`, `last_logical_reads`,
and `last_logical_writes` describe the last execution; `min_elapsed_ms`,
`max_elapsed_ms`, `avg_elapsed_ms`, `avg_cpu_ms`, and `avg_logical_reads` are
the reported extrema/averages. `status` records collection state. DMV values
can reset when plans leave cache or SQL Server restarts; compare snapshots
carefully.

### `fact.fact_blocking`

**Grain:** One blocked session observed at a point in time.

`blocking_key` is the row key. `instance_key`, optional `database_key`, optional
`date_key`, and `collection_run_key` identify context. `collected_at` is the
observation time; `blocking_session_id` and `blocked_session_id` identify the
sessions. `blocking_status`, `wait_type`, `wait_time_ms`,
`blocking_duration_ms`, and `blocked_request_count` describe contention.
Blocking/blocked login, host, and program name fields preserve session context;
`blocking_sql_text`, `blocked_sql_text`, and `resource_description` capture
diagnostic text. `status` records collection state.

### `fact.fact_backup`

**Grain:** One observed SQL Server backup execution for a database.

`backup_key` is the row key. `instance_key`, `database_key`, optional `date_key`,
and `collection_run_key` identify context. `backup_start_at`, `backup_finish_at`,
`backup_type`, and `backup_status` describe the backup. `duration_seconds`,
`backup_size_bytes`, `compressed_backup_size_bytes`,
`physical_device_type`, `backup_set_id`, `media_set_id`, and
`recovery_fork_guid` describe its size and recovery lineage. `is_copy_only`,
`backup_file_name`, and `error_message` provide additional backup details;
`status` is the collector status. The current collector queries latest full
backup history for non-system databases.

### `fact.fact_deadlock`

**Grain:** One distinct deadlock graph per instance.

`deadlock_key` is the row key. `instance_key`, optional `database_key`, optional
`date_key`, and `collection_run_key` identify context. `occurred_at` is the event
time; `deadlock_hash` deduplicates the graph within an instance. `victim_session_id`,
`transaction_count`, `involved_session_count`, `deadlock_type`, and
`resource_count` summarize the event. Victim login, host, program, and SQL text
are diagnostic context; `deadlock_graph` stores the captured graph. `status`
records collection state.

### `fact.fact_sqlagent_job`

**Grain:** One SQL Server Agent job-history outcome (or step record).

`sqlagent_job_key` is the row key. `instance_key`, optional `date_key`, and
`collection_run_key` identify context. `collected_at` is when history was
collected; `job_id`, `job_name`, and `sqlagent_job_enabled` identify the job.
`run_id`, `run_requested_at`, `run_start_at`, `run_finish_at`,
`run_duration_seconds`, and `run_status` describe execution. `retry_attempts`,
`step_id`, `step_name`, and `step_status` describe step/retry detail;
`message` stores SQL Agent output. `status` records collection state. The
collector currently reads job outcome rows (`step_id = 0`) from the preceding
24 hours.

## Monitoring tables

### `monitoring.collection_run`

**Grain:** One collector pipeline execution per instance. **Key:**
`collection_run_key`.

`instance_key`, `execution_id`, `collector_name`, and `collector_version` identify
the execution. `started_at`, `finished_at`, and `duration_seconds` describe its
timing; `status` is `running`, `success`, `partial`, or `failed`.
`metrics_requested`, `metrics_collected`, `records_collected`, and `error_count`
are run counters. `alerts_processed_at` marks completion of alert evaluation;
`created_at` is the row creation time.

### `monitoring.collection_error`

**Grain:** One logged collection error. **Key:** `collection_error_key`.

`collection_run_key` and `instance_key` identify its run and instance;
`metric_key` is optional. `occurred_at`, `error_type`, `error_code`,
`error_message`, and `error_detail` record the failure. `source_component`,
`source_module`, `retry_attempt`, and `is_recoverable` describe its origin and
retry context. `resolved_at` is optional; `created_at` records insertion time.

### `monitoring.alert_event`

**Grain:** An alert lifecycle record for an alert code and target. **Key:**
`alert_event_key`.

`instance_key`, optional `database_key`, `metric_key`, and `collection_run_key`
identify the alert context. `alert_code`, `alert_name`, `severity`, and `message`
describe the rule and condition; `current_value` and `threshold_value` hold the
comparison values. `status` is `open`, `acknowledged`, or `resolved`.
`first_seen_at`, `last_seen_at`, `acknowledged_at`, and `resolved_at` track its
lifecycle; `occurrence_count` tracks repeated observations. `created_at` and
`updated_at` are row lifecycle timestamps.

### `monitoring.system_health`

**Grain:** One current health-state row per component. **Key:**
`system_health_key`; natural key: `component_name`.

`component_type`, `host_name`, and `version` describe the component. `status` is
`unknown`, `healthy`, `degraded`, or `unhealthy`. `last_heartbeat_at`,
`last_success_at`, and `last_error_at` record probe history; `message` is the
latest status detail and `consecutive_failures` tracks the failure streak.
`created_at` and `updated_at` are row lifecycle timestamps.

## Configuration tables

### `config.monitoring_target`

**Grain:** One monitoring configuration per SQL Server instance.

`monitoring_target_key` is the row key; `instance_key` is unique. `enabled`
controls scheduling. `collection_interval_seconds` is the fallback interval;
`connection_timeout_seconds`, `command_timeout_seconds`, and `max_retry_count`
control connection/execution behavior. `priority` orders targets;
`description`, `created_at`, and `updated_at` provide notes and lifecycle.
Connection secrets are not stored in this table.

### `config.collection_schedule`

**Grain:** One schedule definition associated with a monitoring target.

`collection_schedule_key` is the row key; `monitoring_target_key` references the
target. `schedule_name`, `schedule_type`, `interval_seconds`, `cron_expression`,
and `timezone` define an interval or cron schedule. `enabled`, `start_at`,
`end_at`, and `priority` govern activation/selection; `description` and
lifecycle timestamps provide notes and audit context.

### `config.alert_rule`

**Grain:** One threshold rule. **Key:** `alert_rule_key`; natural key:
`alert_code`.

`metric_key` identifies the metric. Optional `instance_key` and `database_key`
scope the rule; null scope applies more broadly according to the alert
procedure. `operator`, `threshold_value`, and `severity` define the condition.
`enabled`, `evaluation_window_seconds`, `consecutive_occurrences`, and
`cooldown_seconds` govern evaluation. `alert_name`, `description`, and
lifecycle timestamps provide display and audit context.

## Related definitions

- [Data model](data-model.md) describes the relationships and ingestion path.
- [Retention](retention.md) describes automated cleanup and backup boundaries.
- Table definitions are grouped under `db/dimensions/`, `db/facts/`,
  `db/monitoring/`, `db/config/`, and `db/ddl/`.

