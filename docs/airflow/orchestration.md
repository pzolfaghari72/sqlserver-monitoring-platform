# Airflow Orchestration

Airflow is the scheduler used by the Compose stack. The collection DAG polls
every minute; `config.monitoring_target` enables/disables a target and provides
timeouts and priority, while `config.collection_schedule` supplies the active
interval or cron cadence. Although `config.monitoring_target` has a
`collection_interval_seconds` column, the current DAG does not use it as a
fallback: a target needs an enabled schedule row to continue collecting after
its initial run. Avoid running the standalone collector loop at the same time
as the Airflow collection DAG for a target.

## Change a target's cadence

Update or insert a schedule row for the target in PostgreSQL. Use
`schedule_type = 'interval'` with `interval_seconds`, or `schedule_type = 'cron'`
with a valid five-field cron expression and IANA timezone. These definitions
are mutually exclusive. Set `enabled`, optional start/end timestamps, and
priority deliberately. The DAG selects one eligible schedule per target in
priority/key order. Verify the next collection in the Airflow UI and check the
corresponding `monitoring.collection_run` timestamps.

## Observe and recover

1. Check Airflow's DAG and task state, then open the task log for the failed
	target or batch.
2. Check SQL Server reachability/credentials and PostgreSQL readiness before
	clearing a failed task.
3. Inspect `monitoring.collection_run` and `monitoring.collection_error` to
	determine whether collection failed entirely or only one collector failed.
4. Retry only after addressing the cause. A retry may create a new run and
	duplicate observations if the original task completed persistence but lost
	its Airflow acknowledgement; review timestamps and run keys first.

The health-check DAG records connectivity state independently of data
collection. Alert processing evaluates only successful or partial runs, in
batches of up to 20. The daily data-quality DAG performs the staging purge and
integrity checks. See [DAG design](dag-design.md) for schedules and task
defaults, and the [operations runbook](../operations/runbook.md) for the wider
stack.
