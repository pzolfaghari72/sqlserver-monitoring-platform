#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
days="${1:-7}"
if ! [[ "$days" =~ ^[0-9]+$ ]]; then
    echo "Usage: $0 [retention-days]" >&2
    exit 1
fi
if [[ ! -d airflow/logs ]]; then
    echo "airflow/logs not found -- nothing to clean."
    exit 0
fi
before=$(find airflow/logs -type f -not -name '.gitkeep' | wc -l)
find airflow/logs -type f -not -name '.gitkeep' -mtime "+${days}" -delete
find airflow/logs -mindepth 1 -type d -empty -delete
after=$(find airflow/logs -type f -not -name '.gitkeep' | wc -l)
echo "Removed $((before - after)) log file(s) older than ${days} day(s). ${after} remaining."