# Docker Compose Deployment

## First startup

Prerequisites are Docker Engine/Desktop with Compose v2, GNU Make, and Bash.
From the repository root run:

```bash
make setup
docker compose ps
make health
```

`make setup` invokes `scripts/bootstrap/setup.sh`, creates `.env` from
`.env.example` only when missing, generates local development secrets, builds
images, and starts the stack. Review `.env` before starting if you need
non-default host ports or SQL Server settings. Startup can take several
minutes while PostgreSQL, SQL Server, Airflow, and the database initializer
become ready.

## Services and dependencies

Compose starts PostgreSQL, the bundled SQL Server Developer instance and its
initializer, database initialization, API, frontend, Grafana, and Airflow
webserver/scheduler plus their one-shot initializers. The collector is invoked
by Airflow; Compose does not start the standalone collector polling loop.

Published host ports default to Grafana `3000`, frontend `3001`, PostgreSQL
`5433`, API `8000`, Airflow `8080`, and SQL Server `1433`. Container-to-container
traffic uses Compose service names and internal ports. The operations portal,
Grafana, Airflow, and API URLs and credentials are listed in the
[root README](../../README.md).

## Everyday commands

```bash
docker compose ps
docker compose logs -f <service>
docker compose up -d --build
make down
```

`make down` removes containers and the Compose network but preserves named
volumes. `make restart` runs down/up. Configuration changes in `.env` require
recreating the affected container. To rerun database initialization against an
existing volume, back up first and then run
`docker compose run --rm database-init`.

`make reset` runs `docker compose down -v --remove-orphans` and permanently
deletes named PostgreSQL, SQL Server, and Grafana data volumes. Use it only for
intentional destructive development resets. Do not use `docker compose down -v`
as a routine rebuild command.
