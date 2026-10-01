import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

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
    StringType,
    IntegerType
)


POSTGRES_JDBC = "org.postgresql:postgresql:42.7.8"


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


# ==========================================================
# KAFKA EVENT SCHEMA
# ==========================================================

event_schema = StructType([

    StructField(
        "event_id",
        StringType(),
        True
    ),

    StructField(
        "event_type",
        StringType(),
        True
    ),

    StructField(
        "user_id",
        StringType(),
        True
    ),

    StructField(
        "asset_id",
        IntegerType(),
        True
    ),

    StructField(
        "timestamp",
        StringType(),
        True
    ),

    StructField(
        "severity",
        StringType(),
        True
    ),

    StructField(
        "source",
        StringType(),
        True
    ),

    StructField(
        "action",
        StringType(),
        True
    ),

    StructField(
        "result",
        StringType(),
        True
    ),

    StructField(
        "ip",
        StringType(),
        True
    ),

    StructField(
        "location",
        StringType(),
        True
    )
])


# ==========================================================
# READ FROM KAFKA
# ==========================================================

kafka_df = (
    spark.readStream
    .format("kafka")
    .option(
        "kafka.bootstrap.servers",
        "localhost:9092"
    )
    .option(
        "subscribe",
        "security-events"
    )
    .option(
        "startingOffsets",
        "latest"
    )
    .load()
)


# ==========================================================
# PARSE JSON
# ==========================================================

events_df = kafka_df.select(
    col("value")
    .cast("string")
    .alias("json_value")
)


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


# ==========================================================
# FINAL STREAM DATA
# ==========================================================

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


# ==========================================================
# POSTGRESQL CONNECTION
# ==========================================================

POSTGRES_URL = (
    "jdbc:postgresql://localhost:5432/cyberguard_dw"
)


POSTGRES_PROPERTIES = {

    "user":
        os.getenv(
            "POSTGRES_USER",
            "postgres"
        ),

    "password":
        os.getenv(
            "POSTGRES_PASSWORD"
        ),

    "driver":
        "org.postgresql.Driver"
}


# ==========================================================
# WRITE STREAMING BATCH TO POSTGRESQL
# ==========================================================

def write_to_postgres(
    batch_df,
    batch_id
):

    print(
        f"\nProcessing streaming batch: {batch_id}"
    )


    # Prevent duplicate event IDs
    batch_df = batch_df.dropDuplicates(
        ["event_id"]
    )


    rows = batch_df.collect()


    if not rows:

        print(
            f"Batch {batch_id} contains no events"
        )

        return


    connection = psycopg2.connect(

        host=os.getenv(
            "POSTGRES_HOST",
            "localhost"
        ),

        port=os.getenv(
            "POSTGRES_PORT",
            "5432"
        ),

        database=os.getenv(
            "POSTGRES_DB",
            "cyberguard_dw"
        ),

        user=os.getenv(
            "POSTGRES_USER",
            "postgres"
        ),

        password=os.getenv(
            "POSTGRES_PASSWORD"
        )
    )


    try:

        cursor = connection.cursor()


        values = [

            (

                row.event_id,

                row.event_type,

                row.user_id,

                row.asset_id,

                row.event_timestamp,

                row.severity,

                row.source,

                row.received_at,

                row.action,

                row.result,

                row.ip,

                row.location

            )

            for row in rows
        ]


        insert_query = """

            INSERT INTO public.live_security_events (

                event_id,
                event_type,
                user_id,
                asset_id,
                event_timestamp,
                severity,
                source,
                received_at,
                action,
                result,
                ip,
                location

            )

            VALUES %s

            ON CONFLICT (event_id)
            DO NOTHING

        """


        execute_values(

            cursor,

            insert_query,

            values

        )


        connection.commit()


        print(

            f"Batch {batch_id} processed successfully: "

            f"{len(values)} events checked"

        )


    except Exception as error:

        connection.rollback()

        print(
            f"Error processing batch {batch_id}: {error}"
        )

        raise


    finally:

        cursor.close()

        connection.close()


# ==========================================================
# START STREAM
# ==========================================================

query = (

    final_df

    .writeStream

    .foreachBatch(
        write_to_postgres
    )

    .outputMode(
        "append"
    )

    .option(
        "checkpointLocation",
        "Data/StreamingCheckpoint"
    )

    .start()
)


print(
    "\nPYSPARK KAFKA → POSTGRESQL STREAMING STARTED"
)

print(
    "Listening to Kafka topic: security-events"
)

print(
    "Writing events to PostgreSQL: "
    "public.live_security_events"
)

print(
    "Duplicate protection: ENABLED"
)

print(
    "Authentication fields: "
    "action, result, ip, location"
)


query.awaitTermination()