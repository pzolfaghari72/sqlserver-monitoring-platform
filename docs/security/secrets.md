# Secrets Management

## Local development

`make setup` creates `.env` from `.env.example` when needed and generates local
passwords and an API secret. `.env` is ignored by Git; keep it out of commits,
screenshots, logs, shell transcripts, support bundles, and issue reports. The
setup script does not overwrite an existing `.env`, so review stale values when
upgrading the project.

The API secret is used as the shared `X-API-Key`. The frontend receives it as
runtime configuration, where it can be inspected by browser users. Use only
with a trusted local audience.

## Shared and production environments

The supplied Compose files pass environment variables to services and are not
a production secret manager. Before any shared deployment:

- Replace every development/default credential, including database role
	bootstrap defaults and web UI passwords.
- Use an external secret manager or platform-native secret mechanism; restrict
	who can read deployment configuration and container environments.
- Use distinct credentials per service, least privilege, rotation, and a
	documented revocation process.
- Set a strong unique API secret and protect API access behind TLS and an
	authenticated ingress. Do not expose the frontend's shared key to untrusted
	browser users.
- Keep database passwords URL-encoded in `POSTGRES_PASSWORD_URLENCODED` when
	they are embedded in the Airflow connection URL; ensure it matches
	`POSTGRES_PASSWORD`.
- Never store SQL Server credentials in `config.monitoring_target`; that table
	intentionally holds operational settings, not secrets.

If a secret is exposed, revoke/rotate it immediately, review access logs, and
remove the exposed copy from the relevant storage and history where feasible.
