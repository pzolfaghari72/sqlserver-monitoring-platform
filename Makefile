PYTHON ?= python3
COMPOSE ?= docker compose
.PHONY: setup up down logs test lint rebuild reset
setup:; bash scripts/bootstrap/setup.sh
up:; $(COMPOSE) up -d --build
down:; $(COMPOSE) down
logs:; $(COMPOSE) logs -f
test:; $(PYTHON) -m pytest -q
lint:; $(PYTHON) -m compileall -q app collector airflow
rebuild:; $(COMPOSE) build --no-cache
reset:; $(COMPOSE) down -v --remove-orphans
