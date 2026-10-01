from kafka import KafkaProducer
import json
import time
import random
import uuid
from datetime import datetime


# =========================================================
# KAFKA CONFIGURATION
# =========================================================

KAFKA_SERVER = "localhost:9092"
TOPIC_NAME = "security-events"


# =========================================================
# KAFKA PRODUCER
# =========================================================

producer = KafkaProducer(
    bootstrap_servers=KAFKA_SERVER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8")
)


# =========================================================
# EVENT CONFIGURATION
# =========================================================

EVENT_TYPES = [
    "authentication_failed",
    "authentication_success",
    "network_activity",
    "endpoint_alert"
]


LOCATIONS = [
    "Bengaluru",
    "Mumbai",
    "Delhi",
    "Hyderabad",
    "Chennai"
]


# =========================================================
# NORMAL EVENT GENERATOR
# =========================================================

def generate_event():

    event_type = random.choice(EVENT_TYPES)

    user_number = random.randint(1, 500)

    user_id = f"U{user_number:04d}"

    asset_id = random.randint(1, 300)

    event = {
        "event_id": str(uuid.uuid4()),

        "event_type": event_type,

        "user_id": user_id,

        "asset_id": asset_id,

        "timestamp": datetime.now().isoformat(),

        "severity": random.choice(
            ["LOW", "MEDIUM", "HIGH"]
        ),

        "source": "kafka_producer"
    }


    # =====================================================
    # AUTHENTICATION EVENT DETAILS
    # =====================================================

    if event_type in [
        "authentication_failed",
        "authentication_success"
    ]:

        event["action"] = "LOGIN"

        event["result"] = (
            "FAILED"
            if event_type == "authentication_failed"
            else "SUCCESS"
        )

        event["ip"] = (
            f"10.120."
            f"{random.randint(0, 255)}."
            f"{random.randint(1, 254)}"
        )

        event["location"] = random.choice(
            LOCATIONS
        )


    return event


# =========================================================
# BRUTE-FORCE ATTACK SIMULATION
# =========================================================

def generate_brute_force_attack():

    # Fixed user for this simulated attack
    user_number = random.randint(1, 500)

    user_id = f"U{user_number:04d}"

    asset_id = random.randint(1, 300)

    attack_ip = (
        f"10.120."
        f"{random.randint(0, 255)}."
        f"{random.randint(1, 254)}"
    )

    attack_location = random.choice(LOCATIONS)


    print("\n")
    print("=" * 60)
    print("!!! SIMULATED BRUTE-FORCE ATTACK STARTED !!!")
    print(f"Target User : {user_id}")
    print(f"Target Asset: {asset_id}")
    print(f"Source IP   : {attack_ip}")
    print(f"Location    : {attack_location}")
    print("Generating 5 failed authentication attempts...")
    print("=" * 60)


    # -----------------------------------------------------
    # Generate 5 failed login attempts
    # -----------------------------------------------------

    for attempt in range(1, 6):

        event = {
            "event_id": str(uuid.uuid4()),

            "event_type": "authentication_failed",

            "user_id": user_id,

            "asset_id": asset_id,

            "timestamp": datetime.now().isoformat(),

            "severity": "HIGH",

            "source": "kafka_attack_simulation",

            "action": "LOGIN",

            "result": "FAILED",

            "ip": attack_ip,

            "location": attack_location
        }


        producer.send(
            TOPIC_NAME,
            value=event
        )

        producer.flush()


        print(
            f"ATTACK EVENT {attempt}/5 SENT | "
            f"User: {user_id} | "
            f"Result: FAILED"
        )


        # Small delay so all events remain
        # inside the detector's 2-minute window
        time.sleep(1)


    print("=" * 60)
    print("!!! BRUTE-FORCE ATTACK SIMULATION COMPLETED !!!")
    print(f"User: {user_id}")
    print("5 failed authentication attempts generated.")
    print("=" * 60)
    print("\n")


# =========================================================
# PRODUCER STARTUP
# =========================================================

print("\n========== KAFKA PRODUCER ==========\n")

print(
    f"Kafka Server: {KAFKA_SERVER}"
)

print(
    f"Topic: {TOPIC_NAME}"
)

print(
    "Generating live security events..."
)

print(
    "Normal events + controlled attack simulation"
)

print(
    "\nAttack simulation:"
)

print(
    "5 failed logins within 2 minutes"
)

print(
    "Expected rule result: HIGH"
)

print(
    "If ML also detects anomaly: CRITICAL"
)

print(
    "\nPress Ctrl+C to stop.\n"
)


# =========================================================
# MAIN PRODUCER LOOP
# =========================================================

try:

    event_counter = 0

    while True:

        event_counter += 1


        # -------------------------------------------------
        # Every 20 normal events, simulate an attack
        # -------------------------------------------------

        if event_counter % 20 == 0:

            generate_brute_force_attack()


        else:

            event = generate_event()

            producer.send(
                TOPIC_NAME,
                value=event
            )

            producer.flush()

            print(
                f"Event sent: {event}"
            )

            time.sleep(2)


except KeyboardInterrupt:

    print(
        "\nKafka Producer Stopped"
    )


finally:

    producer.close()