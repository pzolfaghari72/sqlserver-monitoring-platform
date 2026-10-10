# Coding Standards

## Python

- Keep component boundaries clear: API in `app/`, collection in `collector/`,
	and orchestration in `airflow/dags/`.
- Follow the existing Python style and keep functions focused on one behavior.
- Read configuration through the existing Pydantic settings models; do not
	hard-code credentials or connection details.
- Use parameterized SQL for values. Keep SQL identifiers static/allow-listed
	when they must be interpolated.
- Log actionable context without passwords, API keys, or full connection
	strings. Treat collected query text and error details as potentially
	sensitive.

## Database and telemetry contracts

- Keep schema definitions under `db/` and preserve bootstrap dependency order.
- Give every table a clear grain and enforce important uniqueness and
	referential constraints in SQL.
- Use `dimension.dim_metric.metric_code` consistently across seeds, collector,
	alert rules, Grafana queries, and tests.
- Preserve specialized fact grains rather than flattening events into generic
	metrics. Document cumulative/snapshot semantics and units explicitly.
- Make staging loads safe to retry and scope cleanup to the processed run.

## Tests and documentation

- Add or update behavior-scoped tests for changed contracts.
- Run `make lint` and the relevant tests; use `make validate` when practical.
- Update the docs index and affected component/database/security guides when
	behavior, configuration, permissions, or operational recovery changes.
- Do not commit `.env`, generated caches, database dumps, or other local
	artifacts.

