#!/usr/bin/env bash
set -euo pipefail
: "${POSTGRES_HOST:=postgres}"; : "${POSTGRES_PORT:=5432}"; : "${POSTGRES_USER:=monitoring_user}"; : "${POSTGRES_DB:=sqlserver_monitoring}"
export PGPASSWORD="${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
psql_cmd=(psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1)
run(){ echo "Applying $1"; "${psql_cmd[@]}" -f "$ROOT/$1"; }
run db/init/001_create_database.sql
run db/init/002_create_schemas.sql
run db/init/003_create_roles.sql
run db/init/004_create_extensions.sql
for f in \
	"$ROOT/db/dimensions/dim_server.sql" \
	"$ROOT/db/dimensions/dim_instance.sql" \
	"$ROOT/db/dimensions/dim_database.sql" \
	"$ROOT/db/dimensions/dim_date.sql" \
	"$ROOT/db/dimensions/dim_metric.sql"; do
	run "${f#$ROOT/}"
done
run db/monitoring/monitoring_collection_run.sql
for f in "$ROOT"/db/facts/*.sql; do run "${f#$ROOT/}"; done
run db/config/config_monitoring_target.sql
run db/config/config_collection_schedule.sql
run db/config/config_alert_rule.sql
for f in "$ROOT"/db/ddl/*.sql; do run "${f#$ROOT/}"; done
for f in "$ROOT"/db/monitoring/monitoring_collection_error.sql "$ROOT"/db/monitoring/monitoring_alert_event.sql "$ROOT"/db/monitoring/monitoring_system_health.sql; do run "${f#$ROOT/}"; done
run db/functions/fn_get_metric_value.sql
for f in "$ROOT"/db/procedures/*.sql; do run "${f#$ROOT/}"; done
for f in "$ROOT"/db/views/*.sql; do run "${f#$ROOT/}"; done
for f in "$ROOT"/db/seeds/001_seed_dim_metric.sql "$ROOT"/db/seeds/002_seed_dim_date.sql "$ROOT"/db/seeds/003_seed_alert_rule.sql; do run "${f#$ROOT/}"; done
"${psql_cmd[@]}" -v server_name="${SQLSERVER_HOST:-sqlserver}" -v environment="${ENVIRONMENT:-development}" -v instance_name="${SQLSERVER_INSTANCE_NAME:-MSSQLSERVER}" -v server_port="${SQLSERVER_PORT:-1433}" -f "$ROOT/db/seeds/004_seed_monitoring_target.sql"
run db/init/005_create_monitoring_permissions.sql
echo 'Initialized row counts:'
"${psql_cmd[@]}" -c "SELECT schemaname || '.' || relname AS table_name, n_live_tup AS rows FROM pg_stat_user_tables WHERE schemaname IN ('config','dimension','fact','monitoring','staging') ORDER BY schemaname, relname;"
echo 'Database initialization completed successfully.'
