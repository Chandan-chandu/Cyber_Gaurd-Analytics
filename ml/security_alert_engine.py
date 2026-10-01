import os
from pathlib import Path
from datetime import datetime, timedelta

import psycopg2
from dotenv import load_dotenv

from ml.auth_anomaly_detector import (
    load_model,
    detect_anomaly,
)

from ml.security_rules import (
    check_failed_login_rule,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


def generate_security_alert(events, feature_data):

    rule_result = check_failed_login_rule(events)

    model = load_model()

    ml_result = detect_anomaly(
        model,
        feature_data
    )

    rule_triggered = rule_result["rule_triggered"]
    ml_anomaly = ml_result["is_anomaly"]

    if rule_triggered and ml_anomaly:

        severity = "CRITICAL"

        reason = (
            "Repeated failed authentication attempts "
            "and anomalous user behavior detected."
        )

    elif rule_triggered:

        severity = "HIGH"

        reason = rule_result["reason"]

    elif ml_anomaly:

        severity = "MEDIUM"

        reason = (
            "Authentication behavior is unusual "
            "compared with historical behavior."
        )

    else:

        severity = "LOW"

        reason = (
            "No suspicious authentication behavior detected."
        )

    return {
        "alert_generated": rule_triggered or ml_anomaly,
        "severity": severity,
        "reason": reason,
        "rule_triggered": rule_triggered,
        "ml_anomaly": ml_anomaly,
        "ml_anomaly_score": ml_result["anomaly_score"],
    }


def save_alert_to_postgres(alert):

    connection = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    try:

        cursor = connection.cursor()

        insert_query = """
            INSERT INTO public.security_alerts (
                event_id,
                user_id,
                asset_id,
                alert_type,
                severity,
                reason,
                rule_triggered,
                ml_anomaly,
                ml_anomaly_score,
                status
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING alert_id;
        """

        cursor.execute(
            insert_query,
            (
                alert["event_id"],
                alert["user_id"],
                alert["asset_id"],
                alert["alert_type"],
                alert["severity"],
                alert["reason"],
                alert["rule_triggered"],
                alert["ml_anomaly"],
                alert["ml_anomaly_score"],
                "OPEN",
            ),
        )

        alert_id = cursor.fetchone()[0]

        connection.commit()

        print(
            f"\nAlert saved successfully. "
            f"Alert ID: {alert_id}"
        )

        return alert_id

    except Exception as error:

        connection.rollback()

        print(
            f"\nError saving alert: {error}"
        )

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":

    print(
        "\n========== SECURITY ALERT ENGINE ==========\n"
    )

    base_time = datetime.now()

    test_events = []

    for i in range(5):

        test_events.append(
            {
                "timestamp": base_time
                + timedelta(seconds=i * 15),

                "result": "FAILED",
            }
        )

    test_features = {

        "failed_login_count": 15,

        "successful_login_count": 20,

        "total_login_count": 35,

        "unique_ip_count": 30,

        "unique_location_count": 8,

        "average_login_hour": 2.0,

        "failed_login_rate": 15 / 35,

        "login_frequency": 0.20,
    }

    alert_result = generate_security_alert(
        test_events,
        test_features
    )

    print(
        "Alert generated:",
        alert_result["alert_generated"]
    )

    print(
        "Severity:",
        alert_result["severity"]
    )

    print(
        "Rule triggered:",
        alert_result["rule_triggered"]
    )

    print(
        "ML anomaly:",
        alert_result["ml_anomaly"]
    )

    print(
        "ML anomaly score:",
        round(
            alert_result["ml_anomaly_score"],
            6
        )
    )

    print(
        "Reason:",
        alert_result["reason"]
    )

    if alert_result["alert_generated"]:

        database_alert = {

            "event_id": "TEST-ALERT-001",

            "user_id": "U0001",

            "asset_id": 1,

            "alert_type": "AUTHENTICATION_ANOMALY",

            "severity": alert_result["severity"],

            "reason": alert_result["reason"],

            "rule_triggered":
                alert_result["rule_triggered"],

            "ml_anomaly":
                alert_result["ml_anomaly"],

            "ml_anomaly_score":
                alert_result["ml_anomaly_score"],
        }

        save_alert_to_postgres(
            database_alert
        )