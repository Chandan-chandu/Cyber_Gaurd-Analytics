import os

os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = r"C:\hadoop\bin;" + os.environ["PATH"]

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType
)


spark = (
    SparkSession.builder
    .appName("CyberGuard_Kafka_Streaming")
    .master("local[*]")
    .config(
        "spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0"
    )
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")


# Schema of the cybersecurity events
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
    .option("startingOffsets", "earliest")
    .load()
)


# Kafka value is binary → convert to string
events_df = kafka_df.select(
    col("value").cast("string").alias("json_value")
)


# Convert JSON into structured columns
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


# Display streaming events
query = (
    parsed_events_df
    .writeStream
    .format("console")
    .outputMode("append")
    .option("truncate", False)
    .option("numRows", 20)
    .start()
)


print("PYSPARK KAFKA STREAMING STARTED")
print("Listening to topic: security-events")

query.awaitTermination()