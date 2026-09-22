# Project Review and Corrections — 2026-09-21

The project snapshot was reviewed end-to-end and the baseline was rebuilt around the existing architecture rather than introducing a new platform.

## Main corrections

1. **Database bootstrap** was reordered so dependencies are created before dependent objects. The old split `ALTER TABLE fact...` block was removed; fact tables now declare their `collection_run` foreign keys directly.
2. **Seed/schema mismatches** were removed. Seeds now use the actual dimension/config column contracts.
3. **Duplicate configuration files** at `config/*.yml` were removed. The canonical layout is `config/metrics`, `config/alerts`, `config/servers`, and `config/environments`.
4. **`dim_metric.collection_interval_seconds`** was removed from the metric contract; collection scheduling belongs to target/schedule configuration.
5. **Metric-code drift** between Collector, seeds and the database was corrected.
6. **Stored procedures** are explicitly schema-qualified under `monitoring` and are called using the same qualified names.
7. **Staging-to-fact loading** is idempotent and clears only the processed collection run.
8. **Specialized facts** now have an explicit collector persistence path for waits, blocking, query statistics, backups, deadlocks and SQL Agent executions.
9. **SQL Server databases** are synchronized into `dimension.dim_database` on collection so database-level facts have valid dimension keys.
10. **Airflow** is the orchestration layer. The standalone collector loop was removed from Compose to prevent duplicate collection. The collection DAG polls every minute and uses `config.collection_schedule`/target interval to select due targets.
11. **Alert processing** evaluates server and database metric facts, maintains active alert lifecycle, and resolves conditions that were actually evaluated as clear in the same run.
12. **Grafana** now provisions eight non-empty dashboards using one PostgreSQL datasource UID.
13. **Local end-to-end execution** now includes a SQL Server Developer container and creates `MonitoringDemo` for a self-contained development stack.
14. **API/frontend contracts** were aligned with the database schema and local health checks.
15. **Tests** were repaired; local validation completed with `8 passed, 1 skipped`. The skipped test requires Apache Airflow, which is intentionally installed inside the Airflow image.
16. **Generated caches and snapshot contamination** were excluded from the deliverable.

## Validation limitation

Docker is not installed in the current execution environment, so the actual containers could not be started here. Python syntax, JSON dashboard validity, project structure, and the available local test suite were validated. The final acceptance test is `docker compose up -d --build` followed by the health checks described in `README.md`.
