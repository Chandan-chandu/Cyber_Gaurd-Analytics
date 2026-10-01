import os
import time
from pathlib import Path

import joblib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "auth_isolation_forest.pkl"
)

FEATURE_FILE = (
    PROJECT_ROOT
    / "ml"
    / "features"
    / "authentication_features.csv"
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(PROJECT_ROOT / ".env")


connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
)

engine = create_engine(connection_url)


# ============================================================
# ML FEATURE COLUMNS
# ============================================================

FEATURE_COLUMNS = [
    "failed_login_count",
    "successful_login_count",
    "total_login_count",
    "unique_ip_count",
    "unique_location_count",
    "average_login_hour",
    "failed_login_rate",
    "login_frequency",
]


# ============================================================
# SECURITY THRESHOLDS
# ============================================================

# Failed authentication attempts within the live
# 2-minute detection window.

LOW_FAILED_ATTEMPTS = 1
MEDIUM_FAILED_ATTEMPTS = 3
HIGH_FAILED_ATTEMPTS = 5

DETECTION_WINDOW_MINUTES = 2


# ============================================================
# LOAD ISOLATION FOREST
# ============================================================

def load_model():

    if not MODEL_FILE.exists():

        raise FileNotFoundError(
            f"Isolation Forest model not found: {MODEL_FILE}"
        )

    return joblib.load(MODEL_FILE)


# ============================================================
# LOAD HISTORICAL USER FEATURES
# ============================================================

def load_historical_features():

    if not FEATURE_FILE.exists():

        raise FileNotFoundError(
            f"Authentication feature file not found: "
            f"{FEATURE_FILE}"
        )

    df = pd.read_csv(FEATURE_FILE)

    df["user_id"] = df["user_id"].astype(str)

    return df


# ============================================================
# GET RECENT LIVE AUTHENTICATION EVENTS
# ============================================================

def get_recent_authentication_events():

    query = text("""
        SELECT
            event_id,
            event_type,
            user_id,
            asset_id,
            event_timestamp,
            severity,
            action,
            result,
            ip,
            location,
            received_at
        FROM public.live_security_events
        WHERE event_type IN (
            'authentication_failed',
            'authentication_success'
        )
        AND event_timestamp >=
            CURRENT_TIMESTAMP
            - INTERVAL '2 minutes'
        ORDER BY event_timestamp ASC;
    """)

    with engine.connect() as connection:

        df = pd.read_sql(
            query,
            connection
        )

    if df.empty:

        return df

    df["user_id"] = (
        df["user_id"]
        .astype(str)
    )

    df["event_timestamp"] = pd.to_datetime(
        df["event_timestamp"],
        errors="coerce"
    )

    return df


# ============================================================
# RULE-BASED DETECTION
# ============================================================

def check_failed_login_rule(events):

    failed_events = events[
        events["result"]
        .astype(str)
        .str.upper()
        == "FAILED"
    ].copy()

    failed_count = len(failed_events)

    # --------------------------------------------------------
    # No failed attempts
    # --------------------------------------------------------

    if failed_count == 0:

        return {
            "rule_triggered": False,
            "failed_count": 0,
            "reason": "",
        }

    # --------------------------------------------------------
    # Sort failed events chronologically
    # --------------------------------------------------------

    failed_events = failed_events.sort_values(
        "event_timestamp"
    )

    # --------------------------------------------------------
    # Check for brute-force pattern
    #
    # 5 or more failures inside 2 minutes
    # --------------------------------------------------------

    if failed_count >= HIGH_FAILED_ATTEMPTS:

        for i in range(len(failed_events)):

            window_start = (
                failed_events.iloc[i]
                ["event_timestamp"]
            )

            window_end = (
                window_start
                + pd.Timedelta(
                    minutes=DETECTION_WINDOW_MINUTES
                )
            )

            events_in_window = failed_events[
                (
                    failed_events["event_timestamp"]
                    >= window_start
                )
                &
                (
                    failed_events["event_timestamp"]
                    <= window_end
                )
            ]

            if len(events_in_window) >= HIGH_FAILED_ATTEMPTS:

                return {
                    "rule_triggered": True,
                    "failed_count": len(
                        events_in_window
                    ),
                    "reason": (
                        "5 or more failed authentication "
                        "attempts detected within 2 minutes."
                    ),
                }

    # --------------------------------------------------------
    # Failed attempts exist, but no brute-force threshold
    # --------------------------------------------------------

    return {
        "rule_triggered": False,
        "failed_count": failed_count,
        "reason": (
            f"{failed_count} failed authentication "
            f"attempt(s) detected within the "
            f"live detection window."
        ),
    }


# ============================================================
# BUILD CURRENT USER FEATURES
# ============================================================

def build_live_features(
    historical_row,
    user_events
):

    failed_count = int(
        historical_row[
            "failed_login_count"
        ]
    )

    successful_count = int(
        historical_row[
            "successful_login_count"
        ]
    )

    total_count = int(
        historical_row[
            "total_login_count"
        ]
    )

    unique_ip_count = int(
        historical_row[
            "unique_ip_count"
        ]
    )

    unique_location_count = int(
        historical_row[
            "unique_location_count"
        ]
    )

    average_login_hour = float(
        historical_row[
            "average_login_hour"
        ]
    )

    login_frequency = float(
        historical_row[
            "login_frequency"
        ]
    )

    # --------------------------------------------------------
    # Update historical behavior with live events
    # --------------------------------------------------------

    live_failed = int(
        (
            user_events["result"]
            .astype(str)
            .str.upper()
            == "FAILED"
        ).sum()
    )

    live_successful = int(
        (
            user_events["result"]
            .astype(str)
            .str.upper()
            == "SUCCESS"
        ).sum()
    )

    failed_count += live_failed

    successful_count += live_successful

    total_count += len(user_events)

    # --------------------------------------------------------
    # Add new IPs and locations
    # --------------------------------------------------------

    live_ips = set(
        user_events["ip"]
        .dropna()
        .astype(str)
    )

    live_locations = set(
        user_events["location"]
        .dropna()
        .astype(str)
    )

    unique_ip_count = max(
        unique_ip_count,
        len(live_ips)
    )

    unique_location_count = max(
        unique_location_count,
        len(live_locations)
    )

    # --------------------------------------------------------
    # Update average login hour
    # --------------------------------------------------------

    valid_times = user_events[
        "event_timestamp"
    ].dropna()

    if not valid_times.empty:

        live_average_hour = (
            valid_times.dt.hour
            + valid_times.dt.minute / 60
        ).mean()

        average_login_hour = (
            average_login_hour
            + live_average_hour
        ) / 2

    # --------------------------------------------------------
    # Failed login rate
    # --------------------------------------------------------

    failed_login_rate = (
        failed_count / total_count
        if total_count > 0
        else 0
    )

    return {
        "failed_login_count": failed_count,
        "successful_login_count": successful_count,
        "total_login_count": total_count,
        "unique_ip_count": unique_ip_count,
        "unique_location_count": unique_location_count,
        "average_login_hour": average_login_hour,
        "failed_login_rate": failed_login_rate,
        "login_frequency": login_frequency,
    }


# ============================================================
# ML DETECTION
# ============================================================

def detect_ml_anomaly(
    model,
    feature_data
):

    features = pd.DataFrame(
        [feature_data],
        columns=FEATURE_COLUMNS
    )

    prediction = model.predict(
        features
    )[0]

    score = model.decision_function(
        features
    )[0]

    return {
        "is_anomaly": bool(
            prediction == -1
        ),
        "anomaly_score": float(
            score
        ),
    }


# ============================================================
# DETERMINE SECURITY SEVERITY
# ============================================================

def determine_severity(
    failed_count,
    rule_triggered,
    ml_anomaly
):

    # ========================================================
    # CRITICAL
    #
    # Strong brute-force behavior AND ML anomaly
    # ========================================================

    if (
        rule_triggered
        and ml_anomaly
    ):

        return (
            "CRITICAL",
            (
                "Repeated failed authentication attempts "
                "and anomalous user behavior detected."
            )
        )

    # ========================================================
    # HIGH
    #
    # 5+ failed authentication attempts
    # within the detection window
    # ========================================================

    if rule_triggered:

        return (
            "HIGH",
            (
                "5 or more failed authentication "
                "attempts detected within 2 minutes."
            )
        )

    # ========================================================
    # MEDIUM
    #
    # ML anomaly
    # OR
    # 3-4 failed authentication attempts
    # ========================================================

    if ml_anomaly:

        if failed_count >= MEDIUM_FAILED_ATTEMPTS:

            return (
                "MEDIUM",
                (
                    "Multiple failed authentication "
                    "attempts and anomalous user "
                    "behavior detected."
                )
            )

        return (
            "MEDIUM",
            (
                "Authentication behavior is unusual "
                "compared with historical behavior."
            )
        )

    if (
        failed_count >= MEDIUM_FAILED_ATTEMPTS
    ):

        return (
            "MEDIUM",
            (
                f"{failed_count} failed authentication "
                "attempts detected within the live "
                "detection window."
            )
        )

    # ========================================================
    # LOW
    #
    # 1-2 failed authentication attempts
    # without ML anomaly
    # ========================================================

    if (
        failed_count >= LOW_FAILED_ATTEMPTS
    ):

        return (
            "LOW",
            (
                f"{failed_count} failed authentication "
                "attempt(s) detected. Activity requires "
                "monitoring but does not currently meet "
                "the higher-risk thresholds."
            )
        )

    # ========================================================
    # NO ALERT
    # ========================================================

    return (
        None,
        None
    )


# ============================================================
# CREATE SECURITY ALERT
# ============================================================

def save_alert(
    event,
    severity,
    reason,
    rule_triggered,
    ml_anomaly,
    ml_anomaly_score
):

    query = text("""
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
            status,
            created_at
        )
        SELECT
            :event_id,
            :user_id,
            :asset_id,
            :alert_type,
            :severity,
            :reason,
            :rule_triggered,
            :ml_anomaly,
            :ml_anomaly_score,
            'OPEN',
            CURRENT_TIMESTAMP
        WHERE NOT EXISTS (
            SELECT 1
            FROM public.security_alerts
            WHERE event_id = :event_id
        )
        RETURNING alert_id;
    """)

    values = {
        "event_id": event[
            "event_id"
        ],

        "user_id": str(
            event["user_id"]
        ),

        "asset_id": int(
            event["asset_id"]
        ),

        "alert_type":
            "AUTHENTICATION_ANOMALY",

        "severity":
            severity,

        "reason":
            reason,

        "rule_triggered":
            rule_triggered,

        "ml_anomaly":
            ml_anomaly,

        "ml_anomaly_score":
            ml_anomaly_score,
    }

    with engine.begin() as connection:

        result = connection.execute(
            query,
            values
        )

        row = result.fetchone()

    # --------------------------------------------------------
    # New alert
    # --------------------------------------------------------

    if row:

        print(
            "\nALERT SAVED SUCCESSFULLY"
            f" | Alert ID: {row[0]}"
        )

    # --------------------------------------------------------
    # Duplicate event
    # --------------------------------------------------------

    else:

        print(
            "\nAlert already exists for event "
            f"{event['event_id']}"
        )


# ============================================================
# MAIN DETECTION PROCESS
# ============================================================

def detect_live_alerts():

    print(
        "\n========== "
        "LIVE SECURITY ALERT DETECTOR "
        "==========\n"
    )

    # --------------------------------------------------------
    # Load ML model
    # --------------------------------------------------------

    print(
        "Loading Isolation Forest model..."
    )

    model = load_model()

    print(
        "ML model loaded successfully."
    )

    # --------------------------------------------------------
    # Load historical profiles
    # --------------------------------------------------------

    print(
        "Loading historical "
        "authentication features..."
    )

    historical_features = (
        load_historical_features()
    )

    print(
        "Historical user profiles loaded: "
        f"{len(historical_features)}"
    )

    # --------------------------------------------------------
    # Get live events
    # --------------------------------------------------------

    print(
        "\nChecking recent live "
        "authentication events..."
    )

    live_events = (
        get_recent_authentication_events()
    )

    if live_events.empty:

        print(
            "\nNo authentication events found "
            "in the last 2 minutes."
        )

        return

    print(
        "Recent authentication events: "
        f"{len(live_events)}"
    )

    # --------------------------------------------------------
    # Process each user
    # --------------------------------------------------------

    for user_id, user_events in (
        live_events.groupby("user_id")
    ):

        print(
            f"\nChecking user: {user_id}"
        )

        # ----------------------------------------------------
        # Find historical user profile
        # ----------------------------------------------------

        historical_match = (
            historical_features[
                historical_features["user_id"]
                == user_id
            ]
        )

        if historical_match.empty:

            print(
                "No historical profile found. "
                "Skipping ML detection."
            )

            continue

        historical_row = (
            historical_match.iloc[0]
        )

        # ----------------------------------------------------
        # Rule detection
        # ----------------------------------------------------

        rule_result = (
            check_failed_login_rule(
                user_events
            )
        )

        rule_triggered = (
            rule_result[
                "rule_triggered"
            ]
        )

        failed_count = (
            rule_result[
                "failed_count"
            ]
        )

        # ----------------------------------------------------
        # Build live ML features
        # ----------------------------------------------------

        feature_data = (
            build_live_features(
                historical_row,
                user_events
            )
        )

        # ----------------------------------------------------
        # ML detection
        # ----------------------------------------------------

        ml_result = (
            detect_ml_anomaly(
                model,
                feature_data
            )
        )

        ml_anomaly = (
            ml_result[
                "is_anomaly"
            ]
        )

        anomaly_score = (
            ml_result[
                "anomaly_score"
            ]
        )

        # ----------------------------------------------------
        # Determine final severity
        # ----------------------------------------------------

        severity, reason = (
            determine_severity(
                failed_count,
                rule_triggered,
                ml_anomaly
            )
        )

        # ----------------------------------------------------
        # No alert
        # ----------------------------------------------------

        if severity is None:

            print(
                "No suspicious behavior detected."
            )

            continue

        # ----------------------------------------------------
        # Latest event for this user
        # ----------------------------------------------------

        latest_event = (
            user_events.iloc[-1]
            .to_dict()
        )

        # ----------------------------------------------------
        # Display detection result
        # ----------------------------------------------------

        print(
            "\n----------------------------------------"
        )

        print(
            "ALERT DETECTED"
        )

        print(
            f"Severity: {severity}"
        )

        print(
            f"User: {user_id}"
        )

        print(
            f"Failed attempts: {failed_count}"
        )

        print(
            f"Rule triggered: "
            f"{rule_triggered}"
        )

        print(
            f"ML anomaly: "
            f"{ml_anomaly}"
        )

        print(
            f"ML anomaly score: "
            f"{anomaly_score:.6f}"
        )

        print(
            f"Reason: {reason}"
        )

        print(
            "----------------------------------------"
        )

        # ----------------------------------------------------
        # Save alert
        # ----------------------------------------------------

        save_alert(
            latest_event,
            severity,
            reason,
            rule_triggered,
            ml_anomaly,
            anomaly_score
        )


# ============================================================
# CONTINUOUS RUN
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "=" * 70
    )

    print(
        "CYBERGUARD LIVE ALERT DETECTOR STARTED"
    )

    print(
        "=" * 70
    )

    print(
        "Checking live authentication "
        "events continuously..."
    )

    print(
        "Detection interval: 5 seconds"
    )

    print(
        "Detection window: 2 minutes"
    )

    print(
        "Severity levels: "
        "LOW / MEDIUM / HIGH / CRITICAL"
    )

    print(
        "Press CTRL+C to stop"
    )

    print(
        "=" * 70 + "\n"
    )

    try:

        while True:

            try:

                detect_live_alerts()

            except Exception as error:

                print(
                    f"\nAlert detection error: "
                    f"{error}"
                )

                print(
                    "Retrying in 5 seconds...\n"
                )

            time.sleep(5)

    except KeyboardInterrupt:

        print("\n")

        print(
            "=" * 70
        )

        print(
            "CYBERGUARD LIVE ALERT DETECTOR STOPPED"
        )

        print(
            "=" * 70
        )

    finally:

        engine.dispose()