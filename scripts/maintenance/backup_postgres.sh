#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
if [[ -f .env ]]; then set -a; source .env; set +a; fi
mkdir -p backups
docker compose exec -T postgres pg_dump -U "${POSTGRES_USER:-monitoring_user}" -d "${POSTGRES_DB:-sqlserver_monitoring}" > "backups/sqlserver_monitoring_$(date +%Y%m%d_%H%M%S).sql"
