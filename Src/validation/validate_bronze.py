from pathlib import Path
import pandas as pd


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Bronze data directory
BRONZE_DATA_DIR = PROJECT_ROOT / "Data" / "Bronze"


# Expected columns for each dataset
EXPECTED_COLUMNS = {
    "users": [
        "user_id",
        "department",
        "role",
        "privilege_level",
    ],
    "assets": [
        "asset_id",
        "owner",
        "type",
        "criticality",
    ],
    "auth_logs": [
        "event_id",
        "user_id",
        "timestamp",
        "ip",
        "action",
        "result",
        "location",
    ],
    "network_logs": [
        "event_id",
        "asset_id",
        "timestamp",
        "source_ip",
        "destination_ip",
        "bytes",
    ],
    "endpoint_events": [
        "event_id",
        "asset_id",
        "timestamp",
        "process",
        "severity",
    ],
    "incidents": [
        "incident_id",
        "created_at",
        "severity",
        "status",
        "resolution",
    ],
}


# Primary key for each dataset
PRIMARY_KEYS = {
    "users": "user_id",
    "assets": "asset_id",
    "auth_logs": "event_id",
    "network_logs": "event_id",
    "endpoint_events": "event_id",
    "incidents": "incident_id",
}


def validate_dataset(name, expected_columns, primary_key):

    file_path = BRONZE_DATA_DIR / f"{name}.csv"

    print("\n" + "=" * 60)
    print(f"VALIDATING: {name.upper()}")
    print("=" * 60)

    # Check file exists
    if not file_path.exists():
        print("❌ File not found")
        return

    df = pd.read_csv(file_path)

    # Row count
    print(f"Rows: {len(df):,}")

    # Column validation
    actual_columns = list(df.columns)

    if actual_columns == expected_columns:
        print("✅ Column structure: PASS")
    else:
        print("❌ Column structure: FAIL")
        print(f"Expected: {expected_columns}")
        print(f"Actual:   {actual_columns}")

    # Missing values
    missing_values = df.isnull().sum()
    total_missing = missing_values.sum()

    print(f"Missing values: {total_missing:,}")

    if total_missing == 0:
        print("✅ Missing-value check: PASS")
    else:
        print("⚠️ Missing-value check: REVIEW")

        for column, count in missing_values.items():
            if count > 0:
                print(f"   {column}: {count:,}")

    # Duplicate rows
    duplicate_rows = df.duplicated().sum()

    print(f"Duplicate rows: {duplicate_rows:,}")

    if duplicate_rows == 0:
        print("✅ Duplicate-row check: PASS")
    else:
        print("⚠️ Duplicate-row check: REVIEW")

    # Primary-key duplicates
    duplicate_keys = df[primary_key].duplicated().sum()

    print(f"Duplicate {primary_key}: {duplicate_keys:,}")

    if duplicate_keys == 0:
        print(f"✅ Primary-key check: PASS")
    else:
        print(f"❌ Primary-key check: FAIL")

    # Data types
    print("\nData types:")
    print(df.dtypes)


def main():

    print("\n")
    print("=" * 60)
    print("CYBERGUARD ANALYTICS - BRONZE DATA VALIDATION")
    print("=" * 60)

    for name, columns in EXPECTED_COLUMNS.items():

        primary_key = PRIMARY_KEYS[name]

        validate_dataset(
            name,
            columns,
            primary_key,
        )

    print("\n" + "=" * 60)
    print("BRONZE VALIDATION COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()