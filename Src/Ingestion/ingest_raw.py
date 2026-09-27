from pathlib import Path
import pandas as pd


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Raw data directory
RAW_DATA_DIR = PROJECT_ROOT / "Data" / "Raw"


# Source datasets
DATASETS = {
    "users": "users.csv",
    "assets": "assets.csv",
    "auth_logs": "auth_logs.csv",
    "network_logs": "network_logs.csv",
    "endpoint_events": "endpoint_events.csv",
    "incidents": "incidents.csv",
}


def load_raw_data():
    """Load all raw cybersecurity CSV files into Pandas DataFrames."""

    data = {}

    for name, filename in DATASETS.items():

        file_path = RAW_DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        df = pd.read_csv(file_path)

        data[name] = df

        print(f"\n{name.upper()}")
        print("-" * 40)
        print(f"File: {filename}")
        print(f"Rows: {len(df):,}")
        print(f"Columns: {len(df.columns)}")
        print(f"Column names: {list(df.columns)}")

    return data


if __name__ == "__main__":
    datasets = load_raw_data()

        # Bronze layer directory
    BRONZE_DATA_DIR = PROJECT_ROOT / "Data" / "Bronze"
    BRONZE_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save raw datasets into Bronze layer
    for name, df in datasets.items():
        output_file = BRONZE_DATA_DIR / f"{name}.csv"
        df.to_csv(output_file, index=False)
        print(f"Bronze file created: {output_file}")

    print("\n" + "=" * 50)
    print("RAW DATA INGESTION COMPLETED SUCCESSFULLY")
    print("=" * 50)