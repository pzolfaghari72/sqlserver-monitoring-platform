import json
from pathlib import Path
def test_dashboards_are_provisionable():
    root=Path(__file__).parents[3]
    files=list((root/'grafana/dashboards').glob('**/*.json'))
    assert [f.relative_to(root).as_posix() for f in files] == ['grafana/dashboards/platform_overview.json']
    for f in files:
        data=json.loads(f.read_text())
        assert data['panels']
