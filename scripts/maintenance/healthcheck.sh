#!/usr/bin/env bash
set -euo pipefail
docker compose ps
curl -fsS http://localhost:${API_PORT:-8000}/healthz
curl -fsS http://localhost:${API_PORT:-8000}/readyz
