-- Grafana query variable: metric_code (multi-value; custom All value = ALL)
SELECT m.metric_name || ' [' || m.metric_code || ']' AS "__text", m.metric_code AS "__value"
FROM dimension.dim_metric AS m
WHERE m.is_active
ORDER BY m.category, m.metric_name;
