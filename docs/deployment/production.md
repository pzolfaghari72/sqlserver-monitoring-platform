# Production Readiness

The included Compose deployment is for local development, evaluation, and
controlled small deployments. It is not production-ready by default. A
production owner must design and validate availability, security, capacity,
recovery, and operational ownership for the target environment.

## Required review

- **Ingress and network:** terminate TLS at a reviewed ingress, restrict
	published ports, segment service traffic, and avoid exposing PostgreSQL,
	Airflow administration, or Docker control surfaces publicly.
- **Identity and secrets:** replace all development/default passwords and
	shared service credentials; store secrets in a managed secret system; define
	rotation/revocation; use unique service identities and least-privilege grants.
- **API and frontend:** the portal receives a shared API key in browser
	configuration. Do not expose this model to untrusted users; add a trusted
	authenticated gateway or replace it with a per-user authorization design.
- **Database roles:** review the development role bootstrap and permission
	scripts. The Compose services use the configured PostgreSQL account rather
	than distinct least-privilege service identities.
- **SQL Server access:** validate permissions against supported SQL Server
	versions/features and protect collected query text, login/host metadata, and
	deadlock/blocking detail.
- **Capacity and retention:** size CPU, memory, storage, and collection
	concurrency for the number of targets and cadence. Only staging rows have an
	automated three-day purge; facts and monitoring history currently have no
	retention/partition policy.
- **Availability and recovery:** plan PostgreSQL backups, off-host storage,
	restore drills, RPO/RTO, monitoring of backup completion, and recovery of
	Airflow/Grafana state as required.
- **Operations:** define alert ownership, external notification delivery,
	incident response, patching, image pinning/scanning, log retention, and
	upgrade/migration procedures.

These are design requirements, not guarantees supplied by the repository.
Complete a threat model and deployment review before collecting production
telemetry. Related references: [security model](../security/security-model.md),
[access control](../security/access-control.md), [secrets](../security/secrets.md),
and [backup/recovery](backup-recovery.md).

