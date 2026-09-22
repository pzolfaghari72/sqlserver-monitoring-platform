FROM apache/airflow:2.10.3-python3.12
USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl gnupg unixodbc unixodbc-dev ca-certificates && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list && apt-get update && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && rm -rf /var/lib/apt/lists/*
USER airflow
COPY airflow/requirements.txt /tmp/airflow-requirements.txt
RUN pip install --no-cache-dir -r /tmp/airflow-requirements.txt
COPY collector/requirements.txt /tmp/collector-requirements.txt
RUN pip install --no-cache-dir -r /tmp/collector-requirements.txt
WORKDIR /opt/airflow
ENV PYTHONPATH=/opt/airflow
COPY --chown=airflow:root airflow/dags /opt/airflow/dags
COPY --chown=airflow:root collector /opt/airflow/collector
