SET NOCOUNT ON;

SELECT
    SYSUTCDATETIME() AS captured_at,
    'sqlserver_version_major' AS metric_name,
    CAST(SERVERPROPERTY('ProductMajorVersion') AS DECIMAL(20, 4)) AS metric_value,
    'version' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name

UNION ALL

SELECT
    SYSUTCDATETIME() AS captured_at,
    'sqlserver_cpu_count' AS metric_name,
    CAST(cpu_count AS DECIMAL(20, 4)) AS metric_value,
    'count' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name
FROM sys.dm_os_sys_info

UNION ALL

SELECT
    SYSUTCDATETIME() AS captured_at,
    'sqlserver_physical_memory_mb' AS metric_name,
    CAST(physical_memory_kb / 1024.0 AS DECIMAL(20, 4)) AS metric_value,
    'MB' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name
FROM sys.dm_os_sys_info

UNION ALL

SELECT
    SYSUTCDATETIME() AS captured_at,
    'sqlserver_committed_memory_mb' AS metric_name,
    CAST(committed_kb / 1024.0 AS DECIMAL(20, 4)) AS metric_value,
    'MB' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name
FROM sys.dm_os_sys_info

UNION ALL

SELECT
    SYSUTCDATETIME() AS captured_at,
    'sqlserver_committed_target_memory_mb' AS metric_name,
    CAST(committed_target_kb / 1024.0 AS DECIMAL(20, 4)) AS metric_value,
    'MB' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name
FROM sys.dm_os_sys_info

UNION ALL

SELECT
    SYSUTCDATETIME() AS captured_at,
    'database_count' AS metric_name,
    CAST(COUNT(*) AS DECIMAL(20, 4)) AS metric_value,
    'count' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name
FROM sys.databases

UNION ALL

SELECT
    SYSUTCDATETIME() AS captured_at,
    'database_online_count' AS metric_name,
    CAST(COUNT(*) AS DECIMAL(20, 4)) AS metric_value,
    'count' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name
FROM sys.databases
WHERE state_desc = 'ONLINE'

UNION ALL

SELECT
    SYSUTCDATETIME() AS captured_at,
    'user_connection_count' AS metric_name,
    CAST(COUNT(*) AS DECIMAL(20, 4)) AS metric_value,
    'count' AS metric_unit,
    CAST(NULL AS NVARCHAR(256)) AS database_name,
    CAST(NULL AS NVARCHAR(256)) AS object_name
FROM sys.dm_exec_sessions
WHERE is_user_process = 1;
