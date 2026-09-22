# Database Layer

Initialization is executed by `scripts/bootstrap/init_database.sh` in dependency order:

1. schemas
2. dimensions
3. collection-run control table
4. facts
5. configuration
6. staging
7. monitoring operational tables
8. functions/procedures/views
9. seeds
10. permissions hook

All DDL and seed scripts are idempotent. `staging` is a short-lived landing layer, not a historical reporting store.
