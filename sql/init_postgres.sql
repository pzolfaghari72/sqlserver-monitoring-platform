CREATE TABLE IF NOT EXISTS stg_sql_metrics (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL,
    instance_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC(20, 4),
    metric_unit TEXT,
    database_name TEXT,
    object_name TEXT,
    raw_payload JSONB,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fct_sql_metrics (
    id BIGSERIAL PRIMARY KEY,
    captured_at TIMESTAMPTZ NOT NULL,
    instance_name TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC(20, 4),
    metric_unit TEXT,
    database_name TEXT,
    object_name TEXT,
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_fct_sql_metrics_captured_at
ON fct_sql_metrics (captured_at DESC);

CREATE INDEX IF NOT EXISTS idx_fct_sql_metrics_metric_name
ON fct_sql_metrics (metric_name);

CREATE INDEX IF NOT EXISTS idx_fct_sql_metrics_instance_metric_time
ON fct_sql_metrics (instance_name, metric_name, captured_at DESC);

CREATE INDEX IF NOT EXISTS idx_stg_sql_metrics_captured_at
ON stg_sql_metrics (captured_at DESC);
