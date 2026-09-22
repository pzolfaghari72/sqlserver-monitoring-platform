# SQL Server Monitoring Platform

Production-oriented local stack for monitoring Microsoft SQL Server with PostgreSQL as the monitoring repository, Python Collector, Apache Airflow orchestration, FastAPI API and Grafana dashboards.
# SQL Server Monitoring Platform First Page
<img width="1241" height="881" alt="SQLServerMonitoringPlatform" src="https://github.com/user-attachments/assets/c210f0c1-4408-4887-ab11-b13632b695ca" />

# SQL Server Monitoring Dashboard
<img width="1918" height="1079" alt="GrafanaDashboard" src="https://github.com/user-attachments/assets/269a2896-0778-444f-9c0f-d7ad1efb112f" />

---------------------------------------------------------------------------------------------------------------------------------------------
## Quick Start

```bash
git clone <repository-url>
cd sqlserver_monitoring_platform
make setup
```

`make setup` creates a local `.env` with generated development credentials when one does not exist, builds the containers, initializes PostgreSQL schemas and seeds, provisions the single editable Grafana dashboard, starts Airflow, and starts the frontend/API. It never overwrites an existing `.env`.

Prerequisites: Docker Engine with Compose v2 and GNU Make.

---------------------------------------------------------------------------------------------------------------------------------------------
## URLs

- Grafana platform dashboard: http://localhost:3000/d/sqlserver-platform/sql-server-monitoring-platform
- Airflow: http://localhost:8080
- API docs: http://localhost:8000/api/v1/docs
- Frontend: http://localhost:3001

The default setup monitors the included SQL Server container. To monitor an existing SQL Server instead, edit `.env` after `make setup` and set `SQLSERVER_HOST`, `SQLSERVER_PORT`, `SQLSERVER_USER`, and `SQLSERVER_PASSWORD`, then run `docker compose up -d --build` again.

---------------------------------------------------------------------------------------------------------------------------------------------
## Data flow

SQL Server -> Collector -> staging -> validation/load procedures -> fact tables -> Grafana/API

Specialized operational facts (waits, blocking, query statistics, backups, deadlocks and SQL Agent) are written directly by the collector because they have domain-specific grains; generic server/database metrics use staging-to-fact procedures.

The local `.env` is development-only and ignored by Git. For deployment, use a secret manager and replace all credentials.

If PostgreSQL was initialized before the current schema or seed files were added, rerun the idempotent bootstrap with `docker compose run --rm database-init`. The collector target must use the Compose hostname `sqlserver` in local development.


A production-ready, distributed telemetry, diagnostic, and monitoring platform designed for deep observability and performance tuning of **Microsoft SQL Server (2019/2022)**.

The platform combines a modular **Python Collector**, a **PostgreSQL Dimensional Repository (Star Schema)**, automated ETL & alert orchestration via **Apache Airflow**, a secure **FastAPI** telemetry API, an administrative frontend, and unified operational dashboards in **Grafana**.

---------------------------------------------------------------------------------------------------------------------------------------------
## Architecture & Data Flow

The platform features a **hybrid dual-path ingestion engine** that balances real-time diagnostic needs against historical trend aggregation:
```text
 ┌─────────────────────────────────────────────────────────────┐
 │                Target Microsoft SQL Server                  │
 │      (DMVs, Extended Events, Wait Stats, PerfMon, Agent)    │
 └──────────────────────────────┬──────────────────────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │                 Python Telemetry Collector                  │
 │    (ODBC Driver 18, Modular Domain Engine, Async Pipeline)  │
 └──────────────┬───────────────────────────────┬──────────────┘
   (Direct Operational Facts)            (Raw/Generic Metrics)
                │                               │ 
                ▼                               ▼
 ┌───────────────────────────┐    ┌────────────────────────────┐
 │    Domain Fact Tables     │    │   Ingestion Staging Area   │
 │ • fact_wait_stat          │    │ • staging.server_metric    │
 │ • fact_blocking           │    │ • staging.database_metric  │
 │ • fact_query_stat         │    └─────────────┬──────────────┘
 │ • fact_backup             │                  │
 │ • fact_deadlock           │                  │
 │ • fact_sqlagent_job       │                  │
 │  (sp_load_*_metrics & DQ) │                  │
 └─────────────┬─────────────┘                  │
               │                 ┌────────────────────────────┐
               │                 │  Airflow ELT Orchestration │
               │                 └──────────────┬─────────────┘                  
               │                                │           
               └────────────────┬───────────────┘
                                │
                                ▼
 ┌─────────────────────────────────────────────────────────────┐
 │          PostgreSQL Monitoring Analytical Repository        │
 │       (Dimensional Model: dim_server, dim_db, Views)        │
 └──────────────────────────────┬──────────────────────────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
 ┌───────────────────────────┐     ┌───────────────────────────┐
 │   FastAPI Telemetry API   │     │    Grafana Dashboards     │
 │    & Frontend Portal      │     │  (Platform Overview &     │
 │ (API Key / JWT Protected) │     │   Analytical Drill-downs) │
 └───────────────────────────┘     └───────────────────────────┘
