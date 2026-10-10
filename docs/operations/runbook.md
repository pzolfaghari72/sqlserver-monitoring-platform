# Operations Runbook

## Routine checks

1. Run `docker compose ps` and `make health`; confirm PostgreSQL, API, Airflow,
	and other required services are healthy.
2. In Airflow, check recent runs for collection, health, alert processing, and
	daily data quality.
3. In Grafana, check instance freshness, collection errors, active alerts, and
	SQL Server utilization panels for the required instances.
4. Confirm PostgreSQL backups are being created and copied off-host; test a
	restore on a schedule.

## Collection incident

1. Identify the target and latest `monitoring.collection_run` status.
2. Read the Airflow task log and corresponding `monitoring.collection_error`
	rows. Distinguish target connection failures from individual DMV collector
	failures and PostgreSQL persistence failures.
3. Verify SQL Server host/port reachability from the Airflow container, target
	credentials, required permissions, and PostgreSQL readiness.
4. Correct the cause before retrying. Review the run key first to avoid
	duplicating an observation after a task that persisted data but failed to
	report success.

## Change or stop services

Change environment values in `.env`, then recreate the affected services with
`docker compose up -d --build`. `make down` preserves named volumes. `make
reset` removes named volumes, including PostgreSQL and SQL Server data; use it
only when data loss is intended.

For schema initialization on an existing volume, take a backup first and then
run `docker compose run --rm database-init`. For recovery steps, use the
[backup and recovery guide](../deployment/backup-recovery.md). For symptom-led
triage, use [troubleshooting](troubleshooting.md).
