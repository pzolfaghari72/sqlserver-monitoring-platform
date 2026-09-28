# SQL Server Monitoring Platform

Production-oriented local stack for monitoring Microsoft SQL Server with PostgreSQL as the monitoring repository, Python Collector, Apache Airflow orchestration, FastAPI API and Grafana dashboards.
# SQL Server Monitoring Platform First Page
<img width="1241" height="881" alt="SQLServerMonitoringPlatform" src="https://github.com/user-attachments/assets/c210f0c1-4408-4887-ab11-b13632b695ca" />

# SQL Server Monitoring Dashboard
<img width="1918" height="1079" alt="GrafanaDashboard" src="https://github.com/user-attachments/assets/269a2896-0778-444f-9c0f-d7ad1efb112f" />

============================================================
## Quick Start
============================================================
```bash
git clone <repository-url>
cd sqlserver_monitoring_platform
make setup
```

`make setup` creates a local `.env` with generated development credentials when one does not exist, builds the containers, initializes PostgreSQL schemas and seeds, provisions the single editable Grafana dashboard, starts Airflow, and starts the frontend/API. It never overwrites an existing `.env`.

Prerequisites: Docker Engine with Compose v2 and GNU Make.

============================================================
## URLs
============================================================

- Grafana platform dashboard: http://localhost:3000/d/sqlserver-platform/sql-server-monitoring-platform
- Airflow: http://localhost:8080
- API docs: http://localhost:8000/api/v1/docs
- Frontend: http://localhost:3001

The default setup monitors the included SQL Server container. To monitor an existing SQL Server instead, edit `.env` after `make setup` and set `SQLSERVER_HOST`, `SQLSERVER_PORT`, `SQLSERVER_USER`, and `SQLSERVER_PASSWORD`, then run `docker compose up -d --build` again.

============================================================
## Data flow
============================================================

SQL Server -> Collector -> staging -> validation/load procedures -> fact tables -> Grafana/API

Specialized operational facts (waits, blocking, query statistics, backups, deadlocks and SQL Agent) are written directly by the collector because they have domain-specific grains; generic server/database metrics use staging-to-fact procedures.

The local `.env` is development-only and ignored by Git. For deployment, use a secret manager and replace all credentials.

If PostgreSQL was initialized before the current schema or seed files were added, rerun the idempotent bootstrap with `docker compose run --rm database-init`. The collector target must use the Compose hostname `sqlserver` in local development.


A production-ready, distributed telemetry, diagnostic, and monitoring platform designed for deep observability and performance tuning of **Microsoft SQL Server (2019/2022)**.

The platform combines a modular **Python Collector**, a **PostgreSQL Dimensional Repository (Star Schema)**, automated ETL & alert orchestration via **Apache Airflow**, a secure **FastAPI** telemetry API, an administrative frontend, and unified operational dashboards in **Grafana**.

============================================================
## Architecture & Data Flow
============================================================

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
 │ • fact_deadlock           │                  │ (ELT Load Procedures)
 │ • fact_sqlagent_job       │                  │  sp_load_server_metrics
 └─────────────┬─────────────┘                  │  sp_load_database_metrics
               │                                │
               │                 ┌──────────────┴─────────────┐
               │                 │  Airflow ELT Orchestration │
               │                 │  (Schedules, DQ & Alerts)  │
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




============================================================
## PROJECT STRUCTURE
============================================================


└── sqlserver_monitoring_platform
    ├── .dockerignore
    ├── .env
    ├── .env.example
    ├── .gitignore
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── Makefile
    ├── README.md
    ├── SECURITY.md
    ├── airflow
    │   ├── dags
    │   │   ├── __init__.py
    │   │   ├── alert_processing.py
    │   │   ├── data_quality.py
    │   │   ├── sqlserver_collection.py
    │   │   └── sqlserver_monitoring.py
    │   └── requirements.txt
    ├── app
    │   ├── __init__.py
    │   ├── api
    │   │   ├── __init__.py
    │   │   └── v1
    │   │       ├── __init__.py
    │   │       └── endpoints
    │   │           ├── __init__.py
    │   │           ├── alerts.py
    │   │           ├── health.py
    │   │           └── targets.py
    │   ├── core
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── logging.py
    │   │   └── security.py
    │   ├── main.py
    │   ├── models
    │   │   └── __init__.py
    │   ├── repositories
    │   │   ├── __init__.py
    │   │   ├── alert_repository.py
    │   │   └── target_repository.py
    │   ├── requirements.txt
    │   ├── schemas
    │   │   ├── __init__.py
    │   │   ├── alerts.py
    │   │   └── targets.py
    │   └── services
    │       └── __init__.py
    ├── collector
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── collector.py
    │   ├── core
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── exceptions.py
    │   │   └── logging.py
    │   ├── repository
    │   │   ├── __init__.py
    │   │   └── postgres.py
    │   ├── requirements.txt
    │   ├── services
    │   │   ├── __init__.py
    │   │   └── monitoring.py
    │   └── sqlserver
    │       ├── __init__.py
    │       ├── backups.py
    │       ├── blocking.py
    │       ├── connection.py
    │       ├── database_metrics.py
    │       ├── deadlocks.py
    │       ├── query_metrics.py
    │       ├── server_metrics.py
    │       ├── sql_agent.py
    │       └── wait_stats.py
    ├── config
    │   ├── alerts
    │   ├── alerts.yml
    │   ├── environments
    │   │   ├── development.yml
    │   │   ├── production.yml
    │   │   └── test.yml
    │   ├── metrics
    │   ├── metrics.yml
    │   ├── servers
    │   └── servers.yml
    ├── db
    │   ├── config
    │   │   ├── config_alert_rule.sql
    │   │   ├── config_collection_schedule.sql
    │   │   └── config_monitoring_target.sql
    │   ├── ddl
    │   │   ├── staging_database_metric.sql
    │   │   └── staging_server_metric.sql
    │   ├── dimensions
    │   │   ├── dim_database.sql
    │   │   ├── dim_date.sql
    │   │   ├── dim_instance.sql
    │   │   ├── dim_metric.sql
    │   │   └── dim_server.sql
    │   ├── facts
    │   │   ├── fact_backup.sql
    │   │   ├── fact_blocking.sql
    │   │   ├── fact_database_metric.sql
    │   │   ├── fact_deadlock.sql
    │   │   ├── fact_query_stat.sql
    │   │   ├── fact_server_metric.sql
    │   │   ├── fact_sqlagent_job.sql
    │   │   └── fact_wait_stat.sql
    │   ├── functions
    │   │   ├── fn_get_metric_value.sql
    │   │   └── fn_trg_set_updated_at.sql
    │   ├── init
    │   │   ├── 001_create_database.sql
    │   │   ├── 002_create_schemas.sql
    │   │   ├── 003_create_roles.sql
    │   │   ├── 004_create_extensions.sql
    │   │   └── 005_create_monitoring_permissions.sql
    │   ├── monitoring
    │   │   ├── monitoring_alert_event.sql
    │   │   ├── monitoring_collection_error.sql
    │   │   ├── monitoring_collection_run.sql
    │   │   └── monitoring_system_health.sql
    │   ├── procedures
    │   │   ├── sp_load_database_metrics.sql
    │   │   ├── sp_load_server_metrics.sql
    │   │   └── sp_process_alerts.sql
    │   ├── seeds
    │   │   ├── 001_seed_dim_metric.sql
    │   │   ├── 002_seed_dim_date.sql
    │   │   ├── 003_seed_alert_rule.sql
    │   │   └── 004_seed_monitoring_target.sql
    │   └── views
    │       ├── vw_blocking.sql
    │       ├── vw_database_health.sql
    │       ├── vw_query_performance.sql
    │       ├── vw_server_health.sql
    │       └── vw_wait_statistics.sql
    ├── docker-compose.yml
    ├── docs
    │   ├── airflow
    │   │   ├── dag-design.md
    │   │   └── orchestration.md
    │   ├── architecture
    │   │   ├── components.md
    │   │   ├── data-flow.md
    │   │   ├── overview.md
    │   │   └── security.md
    │   ├── collector
    │   │   ├── collector-design.md
    │   │   └── sqlserver-metrics.md
    │   ├── database
    │   │   ├── data-dictionary.md
    │   │   ├── data-model.md
    │   │   └── retention.md
    │   ├── deployment
    │   │   ├── backup-recovery.md
    │   │   ├── docker.md
    │   │   └── production.md
    │   ├── development
    │   │   ├── coding-standards.md
    │   │   └── development-guide.md
    │   ├── grafana
    │   │   ├── alerting.md
    │   │   └── dashboard-design.md
    │   ├── operations
    │   │   ├── monitoring.md
    │   │   ├── runbook.md
    │   │   └── troubleshooting.md
    │   ├── project-review.md
    │   └── security
    │       ├── access-control.md
    │       ├── secrets.md
    │       └── security-model.md
    ├── frontend
    │   ├── 10-config.sh
    │   ├── app.js
    │   ├── config.js
    │   ├── index.html
    │   └── styles.css
    ├── git
    ├── grafana
    │   ├── alerting
    │   ├── dashboards
    │   │   ├── SQL Server Monitoring Platform.json
    │   │   └── platform_overview.json
    │   ├── provisioning
    │   │   ├── dashboards
    │   │   │   └── provider.yml
    │   │   └── datasources
    │   │       └── postgres.yml
    │   └── queries
    │       ├── backups.sql
    │       ├── blocking.sql
    │       ├── database_health.sql
    │       ├── deadlocks.sql
    │       ├── query_performance.sql
    │       ├── server_health.sql
    │       ├── sql_agent.sql
    │       └── wait_statistics.sql
    ├── infrastructure
    │   ├── airflow
    │   │   └── Dockerfile
    │   ├── app
    │   │   └── Dockerfile
    │   ├── collector
    │   │   └── Dockerfile
    │   ├── frontend
    │   │   └── Dockerfile
    │   ├── grafana
    │   │   ├── Dockerfile
    │   │   └── grafana.ini
    │   └── postgres
    │       ├── Dockerfile
    │       ├── pg_hba.conf
    │       └── postgresql.conf
    ├── requirements.txt
    ├── scripts
    │   ├── bootstrap
    │   │   ├── init_airflow.sh
    │   │   ├── init_database.sh
    │   │   └── setup.sh
    │   ├── deployment
    │   │   ├── deploy.sh
    │   │   ├── restart.sh
    │   │   ├── start.sh
    │   │   └── stop.sh
    │   ├── maintenance
    │   │   ├── backup_postgres.sh
    │   │   ├── cleanup_logs.sh
    │   │   ├── healthcheck.sh
    │   │   └── validate_project.sh
    │   └── security
    │       ├── generate_fernet_key.sh
    │       └── generate_secret.sh
    └── tests
        ├── __init__.py
        ├── e2e
        │   ├── __init__.py
        │   └── test_monitoring_pipeline.py
        ├── fixtures
        ├── integration
        │   ├── __init__.py
        │   ├── airflow
        │   │   ├── __init__.py
        │   │   └── test_dags.py
        │   ├── database
        │   │   ├── __init__.py
        │   │   └── test_schema.py
        │   ├── grafana
        │   │   ├── __init__.py
        │   │   └── test_dashboards.py
        │   └── sqlserver
        │       ├── __init__.py
        │       └── test_connection.py
        └── unit
            ├── __init__.py
            ├── app
            │   ├── __init__.py
            │   ├── test_config.py
            │   └── test_services.py
            └── collector
                ├── __init__.py
                ├── test_config.py
                └── test_metrics.py

75 directories, 194 files
