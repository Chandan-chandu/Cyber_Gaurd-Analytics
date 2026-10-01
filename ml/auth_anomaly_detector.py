from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

MODEL_FILE = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "auth_isolation_forest.pkl"
)


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


def load_model():
    """Load the trained Isolation Forest model."""

    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_FILE}"
        )

    return joblib.load(MODEL_FILE)


def detect_anomaly(model, feature_data):
    """
    Detect whether authentication behavior
    is anomalous.
    """

    features = pd.DataFrame(
        [feature_data],
        columns=FEATURE_COLUMNS
    )

    prediction = model.predict(features)[0]

    score = model.decision_function(features)[0]

    return {
        "is_anomaly": bool(prediction == -1),
        "anomaly_score": float(score),
    }


if __name__ == "__main__":

    print("\n========== LIVE AUTHENTICATION ML DETECTOR ==========\n")

    model = load_model()

    print("Isolation Forest model loaded successfully.")

    # Example authentication behavior.
    # This is only a test event.
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

    result = detect_anomaly(
        model,
        test_features
    )

    print("\nTest authentication behavior:")

    print(f"ML anomaly: {result['is_anomaly']}")
    print(f"Anomaly score: {result['anomaly_score']:.6f}")

    if result["is_anomaly"]:
        print("\nRESULT: ANOMALOUS AUTHENTICATION BEHAVIOR")
    else:
        print("\nRESULT: NORMAL AUTHENTICATION BEHAVIOR")