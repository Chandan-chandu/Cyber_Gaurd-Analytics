# \*\*CyberGuard Analytics\*\*

# 

# \*\*End-to-End Cybersecurity Data Engineering \& Analytics Platform\*\*

# 

# CyberGuard Analytics is an end-to-end cybersecurity data engineering and analytics project designed to ingest, process, validate, transform, store, analyze, and visualize security data from both batch and real-time sources.

# 

# The platform combines a modern data engineering pipeline with real-time Kafka streaming, PostgreSQL, dbt, Apache Airflow, FastAPI, React, and Power BI.

# 

# \---

# 

# \*\*Project Overview\*\*

# 

# CyberGuard Analytics processes cybersecurity data through a layered architecture:

# 

# Raw Data → Bronze → Silver → PostgreSQL → dbt → Gold → Analytics \& Dashboards

# 

# In parallel, real-time security events are generated through Kafka and processed using PySpark Structured Streaming before being stored in PostgreSQL.

# 

# The project demonstrates practical concepts from both Data Engineering and Data Analytics.

# 

# \---

# 

# \*\*Architecture\*\*

# 

# ```text

# &#x20;                   CYBERSECURITY DATA SOURCES

# &#x20;                             │

# &#x20;               ┌─────────────┴─────────────┐

# &#x20;               │                           │

# &#x20;         BATCH CSV DATA              REAL-TIME EVENTS

# &#x20;               │                           │

# &#x20;         Python / Pandas             Kafka Producer

# &#x20;               │                           │

# &#x20;            BRONZE                  Kafka Topic

# &#x20;               │                           │

# &#x20;            PySpark              PySpark Streaming

# &#x20;               │                           │

# &#x20;            SILVER                        │

# &#x20;               │                           │

# &#x20;               └─────────────┬─────────────┘

# &#x20;                             │

# &#x20;                        PostgreSQL

# &#x20;                      Data Warehouse

# &#x20;                             │

# &#x20;                            dbt

# &#x20;                             │

# &#x20;                            GOLD

# &#x20;                             │

# &#x20;             ┌───────────────┴────────────────┐

# &#x20;             │                                │

# &#x20;         Power BI                         FastAPI

# &#x20;                                              │

# &#x20;                                            React

# &#x20;                                              │

# &#x20;                                     Security Dashboard

# 

# &#x20;            Apache Airflow

# &#x20;                   │

# &#x20;                   └── Orchestrates the batch pipeline

