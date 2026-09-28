import os

from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = r"C:\hadoop\bin;" + os.environ["PATH"]

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json,
    col,
    current_timestamp,
    to_timestamp
)
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType
)


# PostgreSQL JDBC driver
POSTGRES_JDBC = (
    "org.postgresql:postgresql:42.7.8"
)


# Start Spark
spark = (
    SparkSession.builder
    .appName("CyberGuard_Kafka_To_PostgreSQL")
    .master("local[*]")
    .config(
        "spark.jars.packages",
        ",".join([
            "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0",
            POSTGRES_JDBC
        ])
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# Kafka event structure
event_schema = StructType([
    StructField("event_id", IntegerType(), True),
    StructField("event_type", StringType(), True),
    StructField("user_id", IntegerType(), True),
    StructField("asset_id", IntegerType(), True),
    StructField("timestamp", StringType(), True),
    StructField("severity", StringType(), True),
    StructField("source", StringType(), True)
])


# Read events from Kafka
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "security-events")
    .option("startingOffsets", "latest")
    .load()
)


# Convert Kafka value to JSON string
events_df = kafka_df.select(
    col("value").cast("string").alias("json_value")
)


# Convert JSON into columns
parsed_events_df = (
    events_df
    .select(
        from_json(
            col("json_value"),
            event_schema
        ).alias("event")
    )
    .select("event.*")
)


# Convert Kafka timestamp string to PostgreSQL timestamp
final_df = (
    parsed_events_df
    .withColumn(
        "event_timestamp",
        to_timestamp(col("timestamp"))
    )
    .drop("timestamp")
    .withColumn(
        "received_at",
        current_timestamp()
    )
)


# PostgreSQL connection
POSTGRES_URL = (
    "jdbc:postgresql://localhost:5432/cyberguard_dw"
)

POSTGRES_PROPERTIES = {
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "driver": "org.postgresql.Driver"
}


# Write each streaming batch to PostgreSQL
def write_to_postgres(batch_df, batch_id):

    print(f"\nProcessing streaming batch: {batch_id}")

    (
        batch_df
        .write
        .jdbc(
            url=POSTGRES_URL,
            table="public.live_security_events",
            mode="append",
            properties=POSTGRES_PROPERTIES
        )
    )

    print(f"Batch {batch_id} written to PostgreSQL")


# Start streaming
query = (
    final_df
    .writeStream
    .foreachBatch(write_to_postgres)
    .outputMode("append")
    .option(
        "checkpointLocation",
        "Data/StreamingCheckpoint"
    )
    .start()
)


print("PYSPARK KAFKA → POSTGRESQL STREAMING STARTED")
print("Listening to Kafka topic: security-events")
print("Writing events to PostgreSQL: public.live_security_events")

query.awaitTermination()