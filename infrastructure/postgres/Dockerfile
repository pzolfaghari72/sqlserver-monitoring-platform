FROM postgres:16-alpine

COPY infrastructure/postgres/postgresql.conf /etc/postgresql/postgresql.conf
COPY infrastructure/postgres/pg_hba.conf /etc/postgresql/pg_hba.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]