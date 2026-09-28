CyberGuard Analytics – Power BI Dashboard

Overview

CyberGuard Analytics includes an interactive Power BI dashboard for monitoring cybersecurity activity and security-related metrics.

The dashboard is connected to the PostgreSQL data warehouse and uses analytical marts created with dbt.

Dashboard Features

The dashboard provides insights into:

- Total Login Attempts
- Failed Login Attempts
- Failed Login Rate
- Total Incidents
- Resolved Incidents
- Incident Resolution Rate
- Failed Login Trends
- Incident Trends
- Incident Status
- Asset Activity Risk
- Suspicious Endpoint Events

## Data Architecture

```text
Raw Data
   ↓
PySpark
   ↓
PostgreSQL Data Warehouse
   ↓
dbt Analytical Marts
   ↓
Power BI Dashboard