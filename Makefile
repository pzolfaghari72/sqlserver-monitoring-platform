PYTHON ?= python3
COMPOSE ?= docker compose

.PHONY: setup up down restart logs test lint validate rebuild reset deploy health backup cleanup-logs generate-secret generate-fernet-key
 
setup:; bash scripts/bootstrap/setup.sh
up:; $(COMPOSE) up -d --build
down:; $(COMPOSE) down
restart: down up
logs:; $(COMPOSE) logs -f
rebuild:; $(COMPOSE) build --no-cache
reset:; $(COMPOSE) down -v --remove-orphans
 
test:; $(PYTHON) -m pytest -q
lint:; $(PYTHON) -m compileall -q app collector airflow

validate:; bash scripts/maintenance/validate_project.sh
 
deploy:; bash scripts/deployment/deploy.sh $(ARGS)
health:; bash scripts/maintenance/healthcheck.sh
backup:; bash scripts/maintenance/backup_postgres.sh
cleanup-logs:; bash scripts/maintenance/cleanup_logs.sh $(ARGS)
 
generate-secret:; bash scripts/security/generate_secret.sh $(ARGS)
generate-fernet-key:; bash scripts/security/generate_fernet_key.sh