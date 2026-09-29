from kafka import KafkaProducer
import json
import time
import random
import uuid
from datetime import datetime


# ============================================================
# KAFKA CONFIGURATION
# ============================================================

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "security-events"


# ============================================================
# KAFKA PRODUCER
# ============================================================

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


# ============================================================
# SECURITY EVENT TYPES
# ============================================================

event_types = [
    "authentication_failed",
    "authentication_success",
    "network_activity",
    "endpoint_alert"
]


# ============================================================
# GENERATE SECURITY EVENT
# ============================================================

def generate_event():

    return {
        # UUID provides a highly collision-resistant event ID
        "event_id": str(uuid.uuid4()),

        "event_type": random.choice(event_types),

        "user_id": random.randint(1, 500),

        "asset_id": random.randint(1, 300),

        "timestamp": datetime.now().isoformat(),

        "severity": random.choice(
            ["LOW", "MEDIUM", "HIGH"]
        ),

        "source": "kafka_producer"
    }


# ============================================================
# START PRODUCER
# ============================================================

print("Kafka Producer Started")

print(
    f"Sending events to topic: {TOPIC_NAME}"
)

print(
    "Event ID generation: UUID"
)


# ============================================================
# SEND EVENTS
# ============================================================

try:

    while True:

        event = generate_event()

        producer.send(
            TOPIC_NAME,
            value=event
        )

        producer.flush()

        print(
            f"Event sent: {event}"
        )

        # Generate one event every 2 seconds
        time.sleep(2)


except KeyboardInterrupt:

    print(
        "\nKafka Producer Stopped"
    )


finally:

    producer.close()