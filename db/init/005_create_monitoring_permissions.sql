/*
===============================================================================
File: 005_create_monitoring_permissions.sql
Purpose:
    Final permission hook for the deployment. The bootstrap database user owns
    all application schemas in the development stack.
Notes:
    Production deployments should replace this with least-privilege grants.
===============================================================================
*/

SELECT 1;
