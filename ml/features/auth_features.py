import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parents[2]

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


def load_authentication_data():
    query = """
        SELECT
            event_id,
            user_id,
            timestamp,
            ip,
            action,
            result,
            location
        FROM silver.auth_logs
    """

    df = pd.read_sql(query, engine)

    return df


def create_authentication_features(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    df["result"] = df["result"].astype(str).str.upper().str.strip()

    df["failed_login"] = (
        df["result"] == "FAILED"
    ).astype(int)

    df["successful_login"] = (
        df["result"] == "SUCCESS"
    ).astype(int)

    df["hour_of_day"] = df["timestamp"].dt.hour

    features = (
        df.groupby("user_id")
        .agg(
            failed_login_count=("failed_login", "sum"),
            successful_login_count=("successful_login", "sum"),
            total_login_count=("event_id", "count"),
            unique_ip_count=("ip", "nunique"),
            unique_location_count=("location", "nunique"),
            average_login_hour=("hour_of_day", "mean"),
        )
        .reset_index()
    )

    features["failed_login_rate"] = (
        features["failed_login_count"]
        / features["total_login_count"]
    )

    features["login_frequency"] = (
        features["total_login_count"]
        / max(
            1,
            (
                df["timestamp"].max() - df["timestamp"].min()
            ).days + 1
        )
    )

    return features


if __name__ == "__main__":

    print("\n========== AUTHENTICATION FEATURE ENGINEERING ==========\n")

    auth_df = load_authentication_data()

    print(f"Authentication records loaded: {len(auth_df):,}")

    feature_df = create_authentication_features(auth_df)

    print(f"Users with features generated: {len(feature_df):,}")

    print("\n========== FEATURE COLUMNS ==========\n")
    print(feature_df.columns.tolist())

    print("\n========== SAMPLE FEATURES ==========\n")
    print(feature_df.head(10).to_string(index=False))

    output_dir = PROJECT_ROOT / "ml" / "features"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "authentication_features.csv"

    feature_df.to_csv(
        output_path,
        index=False
    )

    print(f"\nFeatures saved to:")
    print(output_path)

    engine.dispose()