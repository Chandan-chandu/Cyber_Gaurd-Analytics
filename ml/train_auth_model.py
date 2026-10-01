import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest


PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEATURE_FILE = (
    PROJECT_ROOT
    / "ml"
    / "features"
    / "authentication_features.csv"
)

MODEL_DIR = PROJECT_ROOT / "ml" / "models"

MODEL_FILE = MODEL_DIR / "auth_isolation_forest.pkl"


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


if __name__ == "__main__":

    print("\n========== AUTHENTICATION ANOMALY MODEL ==========\n")

    df = pd.read_csv(FEATURE_FILE)

    print(f"Feature records loaded: {len(df):,}")
    print(f"Features used for training: {len(FEATURE_COLUMNS)}")

    X = df[FEATURE_COLUMNS]

    print("\nTraining Isolation Forest...")

    model = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X)

    df["anomaly_prediction"] = model.predict(X)

    df["anomaly_score"] = model.decision_function(X)

    df["is_anomaly"] = (
        df["anomaly_prediction"] == -1
    ).astype(int)

    anomaly_count = df["is_anomaly"].sum()

    print("\n========== MODEL RESULTS ==========\n")

    print(f"Total users analyzed: {len(df):,}")
    print(f"Anomalous users detected: {anomaly_count:,}")
    print(
        f"Normal users detected: "
        f"{len(df) - anomaly_count:,}"
    )

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    print("\nModel saved to:")
    print(MODEL_FILE)

    results_file = (
        PROJECT_ROOT
        / "ml"
        / "features"
        / "authentication_anomaly_results.csv"
    )

    df.to_csv(
        results_file,
        index=False
    )

    print("\nPrediction results saved to:")
    print(results_file)

    print("\n========== TOP ANOMALIES ==========\n")

    print(
        df[
            [
                "user_id",
                "failed_login_count",
                "failed_login_rate",
                "unique_ip_count",
                "anomaly_score",
                "is_anomaly",
            ]
        ]
        .sort_values("anomaly_score")
        .head(10)
        .to_string(index=False)
    )