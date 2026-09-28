from fastapi import FastAPI
from api.db import get_connection

app = FastAPI(
    title="CyberGuard Analytics API",
    description="Backend API for CyberGuard Analytics",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "CyberGuard Analytics API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/kpis")
def get_security_kpis():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                total_login_attempts,
                failed_login_attempts,
                failed_login_rate_pct,
                total_incidents,
                resolved_incidents,
                incident_resolution_rate_pct,
                total_assets,
                high_criticality_assets,
                total_endpoint_events,
                suspicious_endpoint_events,
                suspicious_endpoint_rate_pct,
                total_network_events,
                total_network_bytes
            FROM analytics.mart_security_kpis
            LIMIT 1
        """)

        row = cursor.fetchone()

        if row is None:
            return {"message": "No KPI data found"}

        columns = [desc[0] for desc in cursor.description]

        return dict(zip(columns, row))

    finally:
        conn.close()