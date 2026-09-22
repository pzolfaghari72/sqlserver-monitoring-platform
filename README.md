# SQL Server Monitoring Platform

Production-oriented local stack for monitoring Microsoft SQL Server with PostgreSQL as the monitoring repository, Python Collector, Apache Airflow orchestration, FastAPI API and Grafana dashboards.

## Quick Start

```bash
git clone <repository-url>
cd sqlserver_monitoring_platform
make setup
```

`make setup` creates a local `.env` with generated development credentials when one does not exist, builds the containers, initializes PostgreSQL schemas and seeds, provisions the single editable Grafana dashboard, starts Airflow, and starts the frontend/API. It never overwrites an existing `.env`.

Prerequisites: Docker Engine with Compose v2 and GNU Make.

## URLs

- Grafana platform dashboard: http://localhost:3000/d/sqlserver-platform/sql-server-monitoring-platform
- Airflow: http://localhost:8080
- API docs: http://localhost:8000/api/v1/docs
- Frontend: http://localhost:3001

The default setup monitors the included SQL Server container. To monitor an existing SQL Server instead, edit `.env` after `make setup` and set `SQLSERVER_HOST`, `SQLSERVER_PORT`, `SQLSERVER_USER`, and `SQLSERVER_PASSWORD`, then run `docker compose up -d --build` again.

## Data flow

SQL Server -> Collector -> staging -> validation/load procedures -> fact tables -> Grafana/API

Specialized operational facts (waits, blocking, query statistics, backups, deadlocks and SQL Agent) are written directly by the collector because they have domain-specific grains; generic server/database metrics use staging-to-fact procedures.

The local `.env` is development-only and ignored by Git. For deployment, use a secret manager and replace all credentials.

If PostgreSQL was initialized before the current schema or seed files were added, rerun the idempotent bootstrap with `docker compose run --rm database-init`. The collector target must use the Compose hostname `sqlserver` in local development.
