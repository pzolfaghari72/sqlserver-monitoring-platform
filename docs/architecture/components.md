# Component Responsibilities

| Component | Source | Responsibility |
|---|---|---|
| SQL Server | External target; bundled Developer instance in Compose | Source of engine, database, backup, query, wait, blocking, deadlock, and SQL Agent telemetry. |
| Collector | `collector/` | Connects to one target, records a collection run, gathers telemetry, persists it to PostgreSQL, and finalizes the run. |
| PostgreSQL | Compose `postgres`; definitions under `db/` | Stores dimensions, staging, facts, configuration, run history, alerts, and health state. |
| Airflow | `airflow/dags/` | Selects due targets, invokes collection, probes connectivity, processes alerts, and runs daily data-quality maintenance. |
| API | `app/` | Provides liveness/readiness checks and authenticated target/alert endpoints. |
| Portal | `frontend/` | Static operations UI that calls the API using runtime container configuration. It is not an independent authentication boundary. |
| Grafana | `grafana/` | Provisions a PostgreSQL datasource and the SQL Server operations dashboard. |

## Runtime relationships

- Airflow's `postgres_default` connection points to PostgreSQL on the Compose
	network. The collection DAG imports the collector package and invokes the
	same monitoring service used by the collector entry point.
- The collector uses SQL Server credentials from its environment and a
	PostgreSQL repository connection. Target identity and host/port are supplied
	by Airflow from the configured dimensions.
- The API and Grafana read operational data from PostgreSQL. The API also
	updates supported target fields and acknowledges active alerts.
- The database initializer applies the SQL definitions and seeds from `db/`;
	it runs as a one-shot Compose service before dependent services start.

The standalone collector loop remains available as a Python entry point, but
Compose does not run it. Airflow is the stack's collection scheduler; running
both schedulers against the same target can duplicate collection.

