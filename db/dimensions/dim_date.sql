/*
===============================================================================
Table: dimension.dim_date
Purpose:
    Calendar dimension for historical reporting.
Grain:
    One row per calendar date.
Key:
    YYYYMMDD integer.
===============================================================================
*/

CREATE TABLE IF NOT EXISTS dimension.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year_number SMALLINT NOT NULL,
    quarter_number SMALLINT NOT NULL,
    month_number SMALLINT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year SMALLINT NOT NULL,
    day_of_month SMALLINT NOT NULL,
    day_of_year SMALLINT NOT NULL,
    day_of_week SMALLINT NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT ck_dim_date_key CHECK(date_key = (EXTRACT(YEAR FROM full_date)::int*10000 + EXTRACT(MONTH FROM full_date)::int*100 + EXTRACT(DAY FROM full_date)::int)),
    CONSTRAINT ck_dim_date_quarter CHECK(quarter_number BETWEEN 1 AND 4),
    CONSTRAINT ck_dim_date_month CHECK(month_number BETWEEN 1 AND 12),
    CONSTRAINT ck_dim_date_week CHECK(week_of_year BETWEEN 1 AND 53),
    CONSTRAINT ck_dim_date_day_of_week CHECK(day_of_week BETWEEN 1 AND 7)
);
CREATE INDEX IF NOT EXISTS ix_dim_date_year_month ON dimension.dim_date(year_number,month_number);
COMMENT ON TABLE dimension.dim_date IS 'Calendar dimension.';
