/*
===============================================================================
Seed: dimension.dim_date
Purpose:
    Populates a reusable calendar range for monitoring history.
===============================================================================
*/

INSERT INTO dimension.dim_date(date_key,full_date,year_number,quarter_number,month_number,month_name,week_of_year,day_of_month,day_of_year,day_of_week,day_name,is_weekend)
SELECT TO_CHAR(d,'YYYYMMDD')::int,d::date,EXTRACT(YEAR FROM d)::smallint,EXTRACT(QUARTER FROM d)::smallint,EXTRACT(MONTH FROM d)::smallint,TO_CHAR(d,'FMMonth'),EXTRACT(WEEK FROM d)::smallint,EXTRACT(DAY FROM d)::smallint,EXTRACT(DOY FROM d)::smallint,EXTRACT(ISODOW FROM d)::smallint,TO_CHAR(d,'FMDay'),EXTRACT(ISODOW FROM d) IN(6,7)
FROM generate_series('2020-01-01'::date,'2035-12-31'::date,'1 day') d
ON CONFLICT(date_key) DO NOTHING;
