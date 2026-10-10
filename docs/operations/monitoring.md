# Monitoring the Monitoring Platform

Use the three operational views together: Compose reports container state,
Airflow reports scheduled work, and PostgreSQL records data/run health.

## Service and API health

```bash
docker compose ps
make health
```

`make health` checks the Compose service list and the API `/healthz` and
`/readyz` endpoints. It does not prove that collection has succeeded or that
all dashboards have fresh data. Review service logs with
`docker compose logs -f <service>`.

## Collection freshness

In Airflow, inspect `sqlserver_collection` and the target's latest task logs.
In PostgreSQL, compare recent `monitoring.collection_run` rows by instance and
inspect `monitoring.collection_error` for per-domain failures. A partial run
can contain useful data while still having failed collectors.

Use Grafana's instance freshness, collection runs/errors, component health, and
active alerts panels to triage. Dashboard time range and selected instance
filters affect what is visible. Wait and query statistics are DMV snapshots;
avoid treating cumulative counters as rates without calculating valid deltas.

## Health and alert lifecycle

The `sqlserver_monitoring` DAG probes active targets every two minutes and
updates `monitoring.system_health`. `alert_processing` evaluates completed
successful/partial runs every two minutes and writes `monitoring.alert_event`.
The API and portal can list/acknowledge active alerts, but the current stack
does not include an external notification delivery service. Acknowledgement is
not resolution; inspect the alert status and last-seen time.

For storage planning, note that only generic staging rows have automated
retention. See [retention](../database/retention.md) and
[troubleshooting](troubleshooting.md).

