import json
import os
from datetime import datetime, timezone

import pendulum
import psycopg2
import pymssql

from airflow.decorators import dag, task


def get_required_env(env_name: str) -> str:
    env_value = os.getenv(env_name)
    if env_value is None or env_value.strip() == "":
        raise ValueError(f"Required environment variable is missing: {env_name}")
    return env_value


def get_postgres_connection():
    return psycopg2.connect(
        host=get_required_env("POSTGRES_HOST"),
        port=int(get_required_env("POSTGRES_PORT")),
        dbname=get_required_env("POSTGRES_DB"),
        user=get_required_env("POSTGRES_USER"),
        password=get_required_env("POSTGRES_PASSWORD"),
    )


def get_sqlserver_connection():
    return pymssql.connect(
        server=get_required_env("SQLSERVER_HOST"),
        port=int(get_required_env("SQLSERVER_PORT")),
        user=get_required_env("SQLSERVER_USER"),
        password=get_required_env("SQLSERVER_PASSWORD"),
        database=get_required_env("SQLSERVER_DB"),
        login_timeout=10,
        timeout=30,
        charset="UTF-8",
    )


@dag(
    dag_id="sqlserver_monitoring_pipeline",
    description="Extract SQL Server metrics and load into PostgreSQL for Grafana monitoring.",
    schedule="*/5 * * * *",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    tags=["sqlserver", "monitoring", "postgres", "grafana"],
)
def sqlserver_monitoring_pipeline():

    @task(
        task_id="extract_stage_and_transform",
        retries=2,
    )
    def extract_stage_and_transform():
        instance_name = get_required_env("INSTANCE_NAME")
        sql_file_path = "/opt/airflow/sql/init_sqlserver.sql"

        if not os.path.exists(sql_file_path):
            raise FileNotFoundError(f"SQL Server query file not found: {sql_file_path}")

        with open(sql_file_path, "r", encoding="utf-8") as sql_file:
            sql_query = sql_file.read()

        if not sql_query.strip():
            raise ValueError("SQL Server query file is empty.")

        extracted_rows = []

        with get_sqlserver_connection() as sqlserver_conn:
            with sqlserver_conn.cursor(as_dict=True) as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()

                for row in rows:
                    captured_at = row.get("captured_at")
                    metric_name = row.get("metric_name")
                    metric_value = row.get("metric_value")
                    metric_unit = row.get("metric_unit")
                    database_name = row.get("database_name")
                    object_name = row.get("object_name")

                    if captured_at is None:
                        captured_at = datetime.now(timezone.utc)

                    if metric_name is None:
                        continue

                    extracted_rows.append(
                        {
                            "captured_at": captured_at,
                            "instance_name": instance_name,
                            "metric_name": str(metric_name),
                            "metric_value": metric_value,
                            "metric_unit": metric_unit,
                            "database_name": database_name,
                            "object_name": object_name,
                            "raw_payload": json.dumps(
                                {
                                    key: str(value) if value is not None else None
                                    for key, value in row.items()
                                },
                                ensure_ascii=False,
                            ),
                        }
                    )

        if not extracted_rows:
            raise ValueError("No metrics extracted from SQL Server.")

        insert_stage_sql = """
            INSERT INTO stg_sql_metrics (
                captured_at,
                instance_name,
                metric_name,
                metric_value,
                metric_unit,
                database_name,
                object_name,
                raw_payload
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        """

        insert_fact_sql = """
            INSERT INTO fct_sql_metrics (
                captured_at,
                instance_name,
                metric_name,
                metric_value,
                metric_unit,
                database_name,
                object_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        with get_postgres_connection() as postgres_conn:
            with postgres_conn.cursor() as cursor:
                for metric in extracted_rows:
                    stage_values = (
                        metric["captured_at"],
                        metric["instance_name"],
                        metric["metric_name"],
                        metric["metric_value"],
                        metric["metric_unit"],
                        metric["database_name"],
                        metric["object_name"],
                        metric["raw_payload"],
                    )

                    fact_values = (
                        metric["captured_at"],
                        metric["instance_name"],
                        metric["metric_name"],
                        metric["metric_value"],
                        metric["metric_unit"],
                        metric["database_name"],
                        metric["object_name"],
                    )

                    cursor.execute(insert_stage_sql, stage_values)
                    cursor.execute(insert_fact_sql, fact_values)

            postgres_conn.commit()

        return {
            "inserted_rows": len(extracted_rows),
            "instance_name": instance_name,
        }

    extract_stage_and_transform()


sqlserver_monitoring_pipeline()
