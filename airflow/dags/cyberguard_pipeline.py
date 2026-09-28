from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="cyberguard_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["cyberguard", "security", "data-engineering"],
) as dag:

    ingest = BashOperator(
        task_id="ingest_data",
        bash_command=(
            "python /opt/cyberguard/Src/Ingestion/ingest_raw.py"
        ),
    )

    bronze_validation = BashOperator(
        task_id="validate_bronze",
        bash_command=(
            "python /opt/cyberguard/Src/validation/validate_bronze.py"
        ),
    )

    silver = BashOperator(
        task_id="transform_silver",
        bash_command=(
            "python /opt/cyberguard/Src/Transformation/transform_silver.py"
        ),
    )

    silver_validation = BashOperator(
        task_id="validate_silver",
        bash_command=(
            "python /opt/cyberguard/Src/validation/validate_silver.py"
        ),
    )

    postgres = BashOperator(
        task_id="load_postgresql",
        bash_command=(
            "python /opt/cyberguard/Src/Database/load_silver_to_postgres.py"
        ),
    )

    dbt = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "dbt build "
            "--project-dir /opt/cyberguard/dbt/cyberguard_dbt "
            "--threads 1"
        ),
    )

    ingest >> bronze_validation >> silver >> silver_validation >> postgres >> dbt