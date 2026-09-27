from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime


KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "security-events"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


event_types = [
    "authentication_failed",
    "authentication_success",
    "network_activity",
    "endpoint_alert"
]


def generate_event():
    return {
        "event_id": random.randint(100000, 999999),
        "event_type": random.choice(event_types),
        "user_id": random.randint(1, 500),
        "asset_id": random.randint(1, 300),
        "timestamp": datetime.now().isoformat(),
        "severity": random.choice(["LOW", "MEDIUM", "HIGH"]),
        "source": "kafka_producer"
    }


print("Kafka Producer Started")
print(f"Sending events to topic: {TOPIC_NAME}")

try:
    while True:
        event = generate_event()

        producer.send(TOPIC_NAME, value=event)
        producer.flush()

        print(f"Event sent: {event}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\nKafka Producer Stopped")

finally:
    producer.close()