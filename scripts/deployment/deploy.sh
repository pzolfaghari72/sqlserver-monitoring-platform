#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

 
if [[ ! -f .env ]]; then
    echo "No .env found. Run scripts/bootstrap/setup.sh first -- it creates .env with generated credentials." >&2
    exit 1
fi
 
if [[ "${1:-}" == "--validate" ]]; then
    echo "Running project validation (syntax, dashboard JSON, tests)..."
    bash scripts/maintenance/validate_project.sh
fi
 
echo "Building images and starting the stack..."
docker compose up -d --build
 
echo
echo "Stack started. Checking application health..."
if ! API_PORT="${API_PORT:-8000}" bash scripts/maintenance/healthcheck.sh; then
    echo "Containers are up but the health check failed -- check 'docker compose logs'." >&2
    exit 1
fi
 
cat <<EOF
 
Deployment complete.
Frontend:  http://localhost:${FRONTEND_PORT:-3001}/
Grafana:   http://localhost:${GRAFANA_PORT:-3000}/d/sqlserver-platform/sql-server-monitoring-platform
Airflow:   http://localhost:${AIRFLOW_PORT:-8080}/
API docs:  http://localhost:${API_PORT:-8000}/api/v1/docs
EOF