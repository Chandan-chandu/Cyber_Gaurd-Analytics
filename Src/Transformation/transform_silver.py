import os
from pathlib import Path

os.environ["HADOOP_HOME"] = r"C:\hadoop"

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, to_timestamp


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRONZE_DATA_DIR = PROJECT_ROOT / "Data" / "Bronze"
SILVER_DATA_DIR = PROJECT_ROOT / "Data" / "Silver"


# Start Spark
spark = (
    SparkSession.builder
    .appName("CyberGuard_Silver_Transformation")
    .master("local[*]")
    .getOrCreate()
)


DATASETS = [
    "users",
    "assets",
    "auth_logs",
    "network_logs",
    "endpoint_events",
    "incidents",
]


def transform_dataset(dataset_name):

    print(f"\nProcessing: {dataset_name}")

    # Read Bronze data
    df = spark.read.option("header", True).csv(
        str(BRONZE_DATA_DIR / f"{dataset_name}.csv")
    )

    # Remove completely duplicate rows
    df = df.dropDuplicates()

    # Trim whitespace from string columns
    for column_name, data_type in df.dtypes:
        if data_type == "string":
            df = df.withColumn(
                column_name,
                trim(col(column_name))
            )

    # Convert timestamp columns
    if dataset_name in ["auth_logs", "network_logs", "endpoint_events"]:
        df = df.withColumn(
            "timestamp",
            to_timestamp(col("timestamp"))
        )

    if dataset_name == "incidents":
        df = df.withColumn(
            "created_at",
            to_timestamp(col("created_at"))
        )

    # Remove records with missing primary keys
    primary_keys = {
        "users": "user_id",
        "assets": "asset_id",
        "auth_logs": "event_id",
        "network_logs": "event_id",
        "endpoint_events": "event_id",
        "incidents": "incident_id",
    }

    primary_key = primary_keys[dataset_name]

    df = df.dropna(subset=[primary_key])

    # Remove duplicate primary keys
    df = df.dropDuplicates([primary_key])

    return df


if __name__ == "__main__":

    SILVER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for dataset in DATASETS:

        df = transform_dataset(dataset)

        print(f"Rows after transformation: {df.count():,}")

        print(f"Schema for {dataset}:")
        df.printSchema()

        # Write Silver data
        output_path = SILVER_DATA_DIR / dataset

        df.write \
            .mode("overwrite") \
            .option("header", True) \
            .csv(str(output_path))

        print(f"Silver data written to: {output_path}")

    print("\nSILVER TRANSFORMATION COMPLETED SUCCESSFULLY")

    spark.stop()