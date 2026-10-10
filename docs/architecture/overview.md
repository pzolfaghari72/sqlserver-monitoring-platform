# Architecture Overview

The platform collects SQL Server telemetry into PostgreSQL, coordinates
collection and maintenance through Apache Airflow, and serves operational views
through Grafana and a FastAPI-backed static portal.

```mermaid
flowchart LR
	SQL[SQL Server] --> COL[Collector]
	AIR[Airflow] --> COL
	COL --> STG[PostgreSQL staging]
	STG --> LOAD[Load procedures]
	LOAD --> FACT[Dimensions and facts]
	COL --> SPEC[Specialized fact persistence]
	SPEC --> FACT
	AIR --> OPS[Health, alerts, data quality]
	OPS --> MON[Monitoring state]
	FACT --> G[Grafana]
	FACT --> API[FastAPI]
	MON --> G
	MON --> API
	API --> WEB[Static portal]
```

The collection DAG polls once per minute. It chooses active targets whose
configured interval or cron schedule is due, then runs a mapped collector task
for each. The collector records each run, synchronizes database dimensions,
collects generic metrics into staging, writes domain-specific observations to
specialized facts, and executes the staging load procedures. Separate DAGs
probe instance connectivity every two minutes, process pending alerts every two
minutes, and run data-quality checks daily.

The Compose stack is designed for local development, evaluation, and controlled
small deployments. See [production readiness](../deployment/production.md)
before exposing it to an untrusted network or relying on it for production
availability.
