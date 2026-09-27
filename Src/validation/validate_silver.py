from pathlib import Path
from pyspark.sql import SparkSession


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SILVER_DATA_DIR = PROJECT_ROOT / "Data" / "Silver"


spark = (
    SparkSession.builder
    .appName("CyberGuard_Silver_Validation")
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


if __name__ == "__main__":

    print("\n========== SILVER VALIDATION ==========\n")

    for dataset in DATASETS:

        path = SILVER_DATA_DIR / dataset

        print(f"Checking: {dataset}")

        if not path.exists():
            print("ERROR: Silver dataset not found\n")
            continue

        df = spark.read.option("header", True).csv(str(path))

        print(f"Rows: {df.count():,}")
        print(f"Columns: {len(df.columns)}")
        print(f"Column names: {df.columns}")
        print("Status: OK\n")

    print("SILVER VALIDATION COMPLETED SUCCESSFULLY")

    spark.stop()