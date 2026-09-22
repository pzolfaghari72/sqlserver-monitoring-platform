/*
===============================================================================
Table: dimension.dim_metric
Purpose:
    Canonical monitoring metric catalog used by the collector, alert engine and dashboards.
Grain:
    One row per monitoring metric definition.
Notes:
    Collection frequency is intentionally not stored here; operational schedules belong
    to config.monitoring_target and config.collection_schedule.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS dimension.dim_metric (
    metric_key BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    metric_code VARCHAR(100) NOT NULL UNIQUE,
    metric_name VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    unit VARCHAR(50),
    data_type VARCHAR(30) NOT NULL,
    aggregation_type VARCHAR(30) NOT NULL,
    warning_threshold DOUBLE PRECISION,
    critical_threshold DOUBLE PRECISION,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_dim_metric_category CHECK(category IN ('server','database','query','wait','blocking','deadlock','backup','sql_agent')),
    CONSTRAINT ck_dim_metric_data_type CHECK(data_type IN ('integer','bigint','decimal','double','boolean','text')),
    CONSTRAINT ck_dim_metric_aggregation CHECK(aggregation_type IN ('avg','sum','min','max','count','latest','delta','none'))
);
CREATE INDEX IF NOT EXISTS ix_dim_metric_category_active ON dimension.dim_metric(category,is_active);
COMMENT ON TABLE dimension.dim_metric IS 'Canonical monitoring metric catalog.';
