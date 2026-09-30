-- Grafana query variable: database_key (multi-value; custom All value = 0)
-- Depends on the instance_key variable.
SELECT d.database_name || ' (' || i.instance_name || ')' AS "__text", d.database_key AS "__value"
FROM dimension.dim_database AS d
JOIN dimension.dim_instance AS i ON i.instance_key = d.instance_key
WHERE d.is_active
  AND i.is_active
  AND (0 IN (${instance_key:csv}) OR d.instance_key IN (${instance_key:csv}))
ORDER BY i.instance_name, d.database_name;
