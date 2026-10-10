# Airflow DAG Design

The DAGs are defined in `airflow/dags/` and use Airflow's TaskFlow API. Compose
uses `LocalExecutor`, a PostgreSQL metadata database, and the `postgres_default`
connection to the monitoring database. DAGs start at 2026-01-01 with
`catchup=False`, so historical intervals are not backfilled.

| DAG | Schedule | Work |
|---|---|---|
| `sqlserver_collection` | Every minute | Reads enabled targets and their active schedule, determines which are due, and dynamically maps a collector task over them. One active DAG run is allowed; task retries are configured once after 30 seconds. |
| `sqlserver_monitoring` | Every two minutes | Dynamically maps a lightweight `SELECT 1` probe over active targets and upserts current state into `monitoring.system_health`. One active DAG run is allowed; tasks retry once after 20 seconds. |
| `alert_processing` | Every two minutes | Selects up to 20 successful/partial collection runs with `alerts_processed_at IS NULL`, calls `monitoring.sp_process_alerts`, and marks each successful run processed. One active DAG run is allowed; tasks retry once after 20 seconds. |
| `data_quality` | Daily at 02:00 UTC | Deletes staging rows older than three days, checks selected fact/dimension references, and rejects server metrics more than five minutes in the future. One active run is allowed; tasks retry once after two minutes. |

## Scheduling behavior

The collection DAG itself is only a one-minute poller. Per-target cadence comes
from `config.collection_schedule`; the selected schedule must be enabled and
inside its optional `start_at`/`end_at` window. Interval schedules compare the
configured number of seconds with the last finished run. Cron schedules are
evaluated in their configured timezone. The target must also be enabled and its
instance and server active.

Keep at least one valid schedule row for every target that should continue to
collect. A target with no schedule has no interval/cron configuration to use
after its initial run. See [orchestration](orchestration.md) for operational
changes and monitoring.

## Failure behavior

Airflow retries transient task failures according to each DAG's defaults. A
collector run may still finish as partial when an individual metric collector
fails; inspect `monitoring.collection_error` and the run status rather than
assuming a green task means every metric succeeded. Alert runs are marked
processed only after the stored procedure and update succeed. Review task logs
and PostgreSQL state together when a DAG repeatedly retries.

