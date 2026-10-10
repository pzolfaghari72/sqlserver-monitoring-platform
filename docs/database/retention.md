# Data Retention

## Automated cleanup

The `data_quality` Airflow DAG runs daily at 02:00 UTC. It deletes rows older
than **three days** from `staging.server_metric` and
`staging.database_metric`, using each row's `loaded_at` timestamp. The staging
load procedures also clear the staging rows for a processed collection run.
The scheduled purge is a safety net for rows left behind by incomplete loads.

The DAG then checks selected fact-to-dimension relationships and rejects
server-metric timestamps more than five minutes in the future. These checks do
not delete historical fact records.

## No fact-table retention policy

There is currently no automated retention or partition-rotation policy for
fact, monitoring, dimension, or configuration tables. In particular, the
three-day staging setting does **not** apply to historical facts, alert events,
collection runs, or collection errors. Their storage will grow over time.
Before a long-running deployment, define retention by data type, legal and
operational requirements, and dashboard lookback needs; test any archival or
purge process against foreign keys and reporting queries.

## Backups

Use `make backup` to write a timestamped PostgreSQL dump under `backups/`.
Backups are not a retention policy and remain on the same host unless copied
elsewhere. Store protected copies off-host and test restore procedures
periodically. See [backup and recovery](../deployment/backup-recovery.md).

