# Architecture Security Boundaries

## Trust boundaries

- The collector and health DAG make outbound connections to SQL Server and
	PostgreSQL using environment-provided credentials.
- Airflow, the API, Grafana, and PostgreSQL are separate Compose services but
	share the default Compose network. Published ports make selected services
	reachable from the host.
- Protected API routes use one shared `X-API-Key`. This is service-level
	authentication, not per-user identity, authorization, or an audit trail of
	individual portal users.
- The static portal receives its API key through runtime frontend
	configuration. A browser user can inspect client-side configuration; do not
	treat this arrangement as safe for an untrusted public audience.

## Deployment limits

The Compose configuration is a development/evaluation baseline, not a hardened
production security architecture. It publishes service ports, has no built-in
TLS termination or network policy, and uses a shared PostgreSQL service
account in the application services. The database role bootstrap also contains
development defaults; those are not production credential provisioning.

Before production use, place the stack behind an authenticated TLS ingress,
restrict service-to-service and host access, provision distinct least-privilege
database identities and rotated secrets, and remove or replace development
credentials. Review [access control](../security/access-control.md),
[secrets](../security/secrets.md), and [production readiness](../deployment/production.md).

