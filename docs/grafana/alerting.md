# Alert Lifecycle

The platform's threshold alerts are implemented in PostgreSQL and Airflow;
they are distinct from Grafana-managed alert rules and notification policies.
This repository does not provision Grafana alert rules or an external
notification channel.

## Evaluation

`alert_processing` runs every two minutes. It selects up to 20 collection runs
with status `success` or `partial` whose `alerts_processed_at` is null, calls
`monitoring.sp_process_alerts(collection_run_key)`, and marks the run processed
after the procedure succeeds. Rules are stored in `config.alert_rule` and
reference metrics in `dimension.dim_metric`; rule fields include comparison
operator, threshold, severity, optional target scope, evaluation window,
consecutive occurrences, and cooldown.

## Lifecycle and acknowledgement

Triggered conditions are represented by `monitoring.alert_event` with status
`open`, `acknowledged`, or `resolved`. Repeated observations update the active
condition and occurrence timestamps/count. The API lists active alerts and
supports acknowledgement; acknowledgement is not resolution. Resolution is
performed by alert evaluation when the configured condition is evaluated as
clear.

The API currently has no per-user identity or acknowledgement audit identity;
it uses a shared API key. No email, paging, webhook, or other notification
delivery service is configured. Operators should review the Grafana active
alerts panel or the API and monitor the Airflow alert DAG for failed processing.

## Troubleshooting

- Check that the relevant alert rule is enabled and points to an active metric.
- Confirm recent successful/partial collection runs and that their
	`alerts_processed_at` is null or has been set after a successful evaluation.
- Inspect Airflow task logs and the stored procedure/database errors.
- Check `monitoring.alert_event` status, `last_seen_at`, and occurrence count.
- Confirm dashboard time range and instance/database filters before concluding
	that an alert is absent.

