# Architecture

SQL Server -> Collector -> PostgreSQL staging/facts -> Grafana/API. Airflow orchestrates collection, quality and alert processing.
