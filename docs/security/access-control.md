# Access Control

## Application API

`GET /healthz` and `GET /readyz` are public liveness/readiness endpoints.
Target and alert endpoints require `X-API-Key`, compared with the configured
application secret:

| Operation | Capability |
|---|---|
| `GET /api/v1/targets` | List configured monitoring targets. |
| `GET /api/v1/targets/{target_id}` | Read one target. |
| `PATCH /api/v1/targets/{target_id}` | Update supported target fields. |
| `GET /api/v1/alerts/active` | Read active alerts, with a limit from 1 to 500. |
| `POST /api/v1/alerts/{alert_event_key}/acknowledge` | Acknowledge an active alert. |

The shared key does not identify an individual user or distinguish read from
write privileges. Because the static portal receives the key at runtime, it
must be treated as a trusted internal UI, not a public multi-user application.
Use an authenticated gateway or replace the authentication model before
exposing it to untrusted users.

## PostgreSQL

`db/init/003_create_roles.sql` creates reader, collector, and ETL group roles
plus functional users with development fallback passwords when those roles do
not already exist. `db/init/005_create_monitoring_permissions.sql` grants
schema/table permissions, but the development Compose services connect using
the configured shared PostgreSQL account. These scripts are not a complete
least-privilege production provisioning flow.

For production, provision separate login identities outside the application
bootstrap, rotate/revoke fallback credentials, scope grants to each service's
actual operations, and review default privileges, procedure/function execute
rights, and ownership. The database owner/admin credentials should not be used
by dashboards or the API.

## SQL Server

Use a dedicated read-oriented monitoring login. The bundled initialization
grants server-state/database metadata visibility and selected `msdb` access for
Agent history. Review DMV, backup, deadlock, and version-specific permissions
on the target instance. Do not use `sa` for collection; do not grant write
permissions unless a separately reviewed feature requires them.

