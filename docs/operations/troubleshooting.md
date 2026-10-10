# Troubleshooting

| Symptom | Checks and response |
|---|---|
| A service is exited or restarting | Run `docker compose ps` and `docker compose logs --tail=200 <service>`. Check `.env`, published port conflicts, health checks, and dependencies. |
| API `/readyz` fails | Check API logs, PostgreSQL health, database-init completion, and PostgreSQL connection values. `/healthz` alone only indicates the API process responds. |
| Airflow UI is unavailable | Check `airflow-webserver`, `airflow-scheduler`, and `airflow-init` logs. Verify metadata DB connectivity, Airflow credentials, and the configured host port. |
| Collection DAG runs but no target is selected | Confirm target/server/instance are active, the target is enabled, and an enabled schedule row is within its start/end window. Check interval/cron fields and the last finished collection run. |
| SQL Server connection fails | Test DNS/routing from the Airflow container, host/port, login/password, encryption/certificate settings, SQL Server health, and firewall rules. Container hostname `localhost` refers to that container, not the host. |
| A collection is partial | Inspect `monitoring.collection_error` by `collection_run_key`. Review the affected DMV/query permissions and SQL Server feature/version requirements. Other collectors may have succeeded. |
| Facts are missing but collection ran | Check staging rows for the run, metric codes in `dimension.dim_metric`, database dimension synchronization, load procedure logs, and whether facts were already loaded/cleared. |
| Grafana shows no data | Confirm datasource health and dashboard time range, instance/database filters, recent fact timestamps, and whether the selected metric is populated. Validate dashboard provisioning logs. |
| A dashboard value looks misleading | Check the panel's unit and query semantics. DMV waits and cached query stats are snapshots/cumulative values, not automatically interval rates. |
| Alerts are not appearing | Confirm enabled `config.alert_rule` rows, supported metric values, successful/partial collection runs, and `alert_processing` task state. Check whether the run has `alerts_processed_at` set. |
| Database changes do not appear | Back up first, then run `docker compose run --rm database-init`. Existing initialization is not a migration strategy for destructive changes. |
| Host port is already in use | Change the corresponding host-side port in `.env` and recreate the service. Container-internal ports remain unchanged. |

Do not publish logs, `.env`, query text, or database dumps without reviewing
them for credentials and sensitive telemetry. See the
[runbook](runbook.md) for incident handling and
[backup/recovery](../deployment/backup-recovery.md) for data recovery.

