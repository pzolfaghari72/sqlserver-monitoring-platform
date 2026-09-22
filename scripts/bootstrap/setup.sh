#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
    cp .env.example .env
    python3 - <<'PY'
from pathlib import Path
import secrets
from urllib.parse import quote

path = Path('.env')
values = {
    'APP_SECRET_KEY': secrets.token_urlsafe(32),
    'GRAFANA_ADMIN_PASSWORD': secrets.token_urlsafe(24),
    'AIRFLOW_ADMIN_PASSWORD': secrets.token_urlsafe(24),
    'POSTGRES_PASSWORD': secrets.token_urlsafe(24),
    'SQLSERVER_PASSWORD': f'Monitoring_{secrets.token_urlsafe(18)}!1',
    'SQLSERVER_SA_PASSWORD': f'Monitoring_{secrets.token_urlsafe(18)}!1',
}
lines = []
for line in path.read_text().splitlines():
    key = line.split('=', 1)[0] if '=' in line else ''
    if key in values:
        line = f'{key}={values[key]}'
    if key == 'POSTGRES_PASSWORD_URLENCODED':
        line = f'{key}={quote(values["POSTGRES_PASSWORD"], safe="")}'
    lines.append(line)
path.write_text('\n'.join(lines) + '\n')
PY
    echo "Created .env with generated development credentials."
else
    echo "Using existing .env."
fi

docker compose up -d --build

cat <<'EOF'

SQL Server Monitoring Platform is starting.
Frontend:  http://localhost:3001/
Grafana:   http://localhost:3000/d/sqlserver-platform/sql-server-monitoring-platform
Airflow:   http://localhost:8080/
API docs:  http://localhost:8000/api/v1/docs

Use 'make logs' to follow startup and collection activity.
EOF
