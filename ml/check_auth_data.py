import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parents[1]

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


df = pd.read_sql(
    "SELECT * FROM silver.auth_logs LIMIT 10",
    engine
)


print("\n========== AUTHENTICATION DATA ==========\n")
print(df.to_string(index=False))

print("\n========== COLUMNS ==========\n")
print(df.columns.tolist())

print("\n========== ROW COUNT CHECK ==========\n")
print(f"Rows displayed: {len(df)}")


engine.dispose()