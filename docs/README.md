# Documentation

Use the guides below as the project reference. The root [README](../README.md)
contains the quick start, configuration summary, URLs, and common commands.

## Architecture and data

- [Architecture overview](architecture/overview.md)
- [Component responsibilities](architecture/components.md)
- [Data flow](architecture/data-flow.md)
- [Architecture security boundaries](architecture/security.md)
- [Data model](database/data-model.md)
- [Data dictionary](database/data-dictionary.md)
- [Retention and backup boundaries](database/retention.md)

## Running the platform

- [Docker deployment](deployment/docker.md)
- [Production readiness](deployment/production.md)
- [Backup and recovery](deployment/backup-recovery.md)
- [Operations runbook](operations/runbook.md)
- [Monitoring](operations/monitoring.md)
- [Troubleshooting](operations/troubleshooting.md)

## Components

- [Collector design](collector/collector-design.md)
- [Collected SQL Server metrics](collector/sqlserver-metrics.md)
- [Airflow DAG design](airflow/dag-design.md)
- [Airflow orchestration](airflow/orchestration.md)
- [Grafana dashboard design](grafana/dashboard-design.md)
- [Alert lifecycle](grafana/alerting.md)

## Security and development

- [Security model](security/security-model.md)
- [Access control](security/access-control.md)
- [Secrets](security/secrets.md)
- [Development guide](development/development-guide.md)
- [Coding standards](development/coding-standards.md)
- [Contributing](../CONTRIBUTING.md)

## Source of truth

Documentation describes the current implementation, but SQL definitions,
application code, Compose configuration, and provisioned dashboard files are
authoritative when details change. Update the relevant guide whenever a
behavioral contract changes.