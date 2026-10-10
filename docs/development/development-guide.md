# Development Guide

## Prerequisites

The complete stack is run with Docker Engine/Desktop and Docker Compose v2.
GNU Make and Bash are used by the documented workflows. Python 3.12 is used in
the application/collector images; local Python is needed only for editor
support and running host-side tests.

## Start locally

From the repository root:

```bash
make setup
make health
```

`make setup` creates `.env` if absent, builds images, and starts the stack. Use
`make logs` to follow service output and `docker compose ps` to inspect state.
The first startup can take several minutes. The bundled SQL Server target is
reachable to containers as `sqlserver`; host-side ports and service URLs are
listed in the [root README](../../README.md).

## Validate changes

```bash
make lint
make test
```

`make lint` runs Python `compileall` over `app`, `collector`, and `airflow`.
`make test` runs pytest using `python3` (or set `PYTHON=/path/to/python`).
`make validate` also runs project validation, including dashboard JSON checks.
Some integration/DAG checks require dependencies or services available only in
the corresponding containers; report those prerequisites when a check cannot
run locally.

## Change workflow

1. Identify the owning component and its data/API contract.
2. Update source, SQL definitions/seeds, and affected docs together.
3. Keep metric codes, table names, endpoint schemas, and dashboard queries
	synchronized.
4. Run the narrow test first, then the relevant broader checks.
5. For database changes on an existing volume, back up data and run
	`docker compose run --rm database-init` deliberately; initialization is not
	a substitute for a migration plan.

Avoid `make reset` unless deleting local PostgreSQL and SQL Server volumes is
intentional.

