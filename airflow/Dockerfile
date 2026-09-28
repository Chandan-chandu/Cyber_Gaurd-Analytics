FROM apache/airflow:3.3.2-python3.12

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        default-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH="${JAVA_HOME}/bin:${PATH}"

USER airflow

RUN pip install --no-cache-dir \
    pyspark==4.2.0 \
    dbt-core==1.12.5 \
    dbt-postgres==1.11.0 \
    "pandas<3.0" \
    numpy \
    python-dotenv \
    psycopg2-binary \
    sqlalchemy