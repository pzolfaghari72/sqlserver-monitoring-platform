-- Grafana query variable: instance_key (multi-value; custom All value = 0)
SELECT i.instance_name AS "__text", i.instance_key AS "__value"
FROM dimension.dim_instance AS i
WHERE i.is_active
ORDER BY i.instance_name;
