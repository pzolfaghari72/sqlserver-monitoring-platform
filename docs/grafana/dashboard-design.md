# Grafana

The SQL Server Monitoring folder provisions one editable dashboard from JSON. The SQL Server Operations overview uses the PostgreSQL datasource UID `monitoring-postgres` and presents instance freshness, prioritized alert triage, component health, utilization and backup indicators, wait statistics, SQL Agent outcomes, and database/log growth. The dashboard defaults to a 24-hour view and refreshes every minute; the server-metric selector is single-select to avoid mixing incompatible units. Panel descriptions document interpretation caveats where source semantics need care.
