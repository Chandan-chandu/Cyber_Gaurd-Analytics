from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db import get_connection


app = FastAPI(
    title="CyberGuard Analytics API",
    description="Backend API for CyberGuard Analytics",
    version="1.0.0"
)


# ---------------------------------------------------------
# CORS CONFIGURATION
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# ROOT
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "CyberGuard Analytics API is running"
    }


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# ---------------------------------------------------------
# SECURITY KPIs
# ---------------------------------------------------------

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
            return {
                "message": "No KPI data found"
            }

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        return dict(zip(columns, row))

    finally:
        conn.close()


# ---------------------------------------------------------
# AUTHENTICATION TRENDS
# ---------------------------------------------------------

@app.get("/authentication-trends")
def get_authentication_trends():

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                date_day,
                total_login_attempts,
                failed_login_attempts,
                successful_login_attempts,
                failed_login_rate_pct
            FROM analytics.mart_authentication_trends
            ORDER BY date_day
        """)

        rows = cursor.fetchall()

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        conn.close()


# ---------------------------------------------------------
# INCIDENT ANALYSIS
# ---------------------------------------------------------

@app.get("/incident-analysis")
def get_incident_analysis():

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                date_day,
                severity,
                status,
                incident_count,
                closed_incident_count
            FROM analytics.mart_incident_analysis
            ORDER BY date_day, severity, status
        """)

        rows = cursor.fetchall()

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        conn.close()


# ---------------------------------------------------------
# ASSET SECURITY ANALYSIS
# ---------------------------------------------------------

@app.get("/asset-security-analysis")
def get_asset_security_analysis():

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                asset_id,
                owner,
                type,
                criticality,
                network_event_count,
                total_network_bytes,
                endpoint_event_count,
                suspicious_endpoint_event_count,
                activity_risk_indicator
            FROM analytics.mart_asset_security_analysis
            ORDER BY activity_risk_indicator DESC
        """)

        rows = cursor.fetchall()

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        conn.close()


# ---------------------------------------------------------
# SUSPICIOUS ENDPOINT EVENTS
# ---------------------------------------------------------

@app.get("/suspicious-event-analysis")
def get_suspicious_event_analysis():

    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                date_day,
                asset_id,
                process,
                severity,
                suspicious_event_count
            FROM analytics.mart_suspicious_event_analysis
            ORDER BY date_day, severity, asset_id
        """)

        rows = cursor.fetchall()

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        conn.close()