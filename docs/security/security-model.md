# Security Model

## Current controls

- `.env` is ignored by Git and supplies local Compose credentials and the API
	key. The bootstrap script generates development values on first setup.
- Pydantic `SecretStr` protects collector password representations; connection
	strings URL/ODBC-escape credentials when constructing connections.
- Protected API endpoints require the shared `X-API-Key`; only health and
	readiness endpoints are public.
- The API limits its data operations to target listing/lookup/update and active
	alert listing/acknowledgement. It does not provide arbitrary SQL execution.
- SQL Server collection uses a dedicated monitoring login in the bundled
	development SQL Server setup rather than the `sa` login.

## Important limitations

These controls do not make the supplied Compose stack production-hardened. It
has no built-in TLS, per-user API identities, role-based API authorization,
secret rotation workflow, network segmentation, or high-availability design.
The frontend key is delivered to browser code and is therefore visible to its
users. PostgreSQL services use the configured shared Compose credentials; the
database role bootstrap contains development fallback credentials and is not a
production account-provisioning mechanism.

Do not expose the portal/API or database/admin ports to an untrusted network.
Before production use, review the [access-control guide](access-control.md),
[secrets guide](secrets.md), and [production checklist](../deployment/production.md).

