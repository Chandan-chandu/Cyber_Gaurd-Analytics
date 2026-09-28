from pathlib import Path

import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_DATA_DIR = PROJECT_ROOT / "Data" / "Silver"


# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")


# PostgreSQL connection
connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
)

engine = create_engine(connection_url)


# Datasets to load
DATASETS = [
    "users",
    "assets",
    "auth_logs",
    "network_logs",
    "endpoint_events",
    "incidents",
]


def load_dataset(dataset_name, connection):

    print(f"\nLoading: {dataset_name}")

    dataset_path = SILVER_DATA_DIR / dataset_name

    # Read all Spark-generated CSV part files
    csv_files = list(dataset_path.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in {dataset_path}"
        )

    dataframes = [
        pd.read_csv(file)
        for file in csv_files
    ]

    df = pd.concat(dataframes, ignore_index=True)

    # Convert timestamp columns
    if dataset_name in [
        "auth_logs",
        "network_logs",
        "endpoint_events",
    ]:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

    if dataset_name == "incidents":
        df["created_at"] = pd.to_datetime(
            df["created_at"],
            errors="coerce"
        )

    # Remove existing data without dropping the table.
    # This preserves dbt views that depend on the Silver tables.
    connection.execute(
        text(f'DELETE FROM silver."{dataset_name}"')
    )

    # Reload the current Silver dataset
    df.to_sql(
        name=dataset_name,
        con=connection,
        schema="silver",
        if_exists="append",
        index=False,
    )

    print(f"Rows loaded: {len(df):,}")


if __name__ == "__main__":

    print("\n========== SILVER → POSTGRESQL ==========\n")

    # Check PostgreSQL connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    print("POSTGRESQL CONNECTION SUCCESSFUL")

    # Delete and reload all Silver tables in one transaction.
    with engine.begin() as connection:

        for dataset in DATASETS:
            load_dataset(dataset, connection)

    print("\nSILVER DATA LOADED INTO POSTGRESQL SUCCESSFULLY")

    engine.dispose()