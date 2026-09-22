#!/usr/bin/env bash
set -euo pipefail
python -m compileall -q app collector airflow
python - <<'PY'
import json
from pathlib import Path
for path in Path('grafana/dashboards').glob('*.json'):
    data=json.loads(path.read_text())
    assert data.get('panels'), f'No panels: {path}'
print('Grafana dashboard validation: OK')
PY
python -m pytest -q
