# Grafana Dashboard Design

Provisioning is file-based. `grafana/provisioning/datasources/` defines the
PostgreSQL datasource with UID `monitoring-postgres`, and
`grafana/provisioning/dashboards/provider.yml` loads the editable dashboard
JSON from `grafana/dashboards/` into the `SQL Server Monitoring` folder.

The SQL Server Operations overview defaults to a 24-hour range and refreshes
every minute. Its single-select controls filter instances, databases, and one
server metric at a time; single selection avoids comparing incompatible units.
Panels cover instance freshness, component health, active alerts, collection
runs/errors, server metrics, wait statistics, CPU/memory averages, backup
freshness, SQL Agent outcomes, and database/log sizes.

## Query and interpretation notes

- Panel SQL is currently stored inline in dashboard JSON. The separate
	`grafana/queries/` catalog is reference material and is not provisioned as
	dashboards.
- The dashboard reads the monitoring PostgreSQL database; it does not query
	SQL Server directly.
- Wait statistics and query-stat values are sourced from SQL Server DMVs and
	can be cumulative or resettable. Do not interpret them as rates without
	deriving valid deltas.
- Database size and log size are file sizes, not log-space usage percentage.
- Backup panels reflect collected SQL Server backup history and do not verify
	that a backup file exists or can be restored.
- Empty panels can indicate an empty time range, filters with no matching
	facts, a datasource/provisioning issue, or a collector that cannot access a
	SQL Server DMV. Check the underlying fact timestamps and collection errors.

No Grafana-managed alert rules or notification policies are provisioned by
this repository. The platform's threshold alerts are evaluated by Airflow and
stored in `monitoring.alert_event`; see the [alert lifecycle](alerting.md).
