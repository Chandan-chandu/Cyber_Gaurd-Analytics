WITH authentication_metrics AS (
    SELECT
        COUNT(*) AS total_login_attempts,
        SUM(
            CASE
                WHEN LOWER(result) = 'failed' THEN 1
                ELSE 0
            END
        ) AS failed_login_attempts
    FROM {{ ref('int_authentication') }}
),

privileged_metrics AS (
    SELECT
        COUNT(*) AS privileged_activity_count
    FROM {{ ref('int_privileged_activity') }}
),

incident_metrics AS (
    SELECT
        COUNT(*) AS incident_volume
    FROM {{ ref('int_incident_metrics') }}
),

asset_metrics AS (
    SELECT
        COUNT(*) AS total_assets,
        SUM(
            CASE
                WHEN UPPER(criticality) = 'HIGH' THEN 1
                ELSE 0
            END
        ) AS high_criticality_assets,
        SUM(high_severity_endpoint_count) AS high_severity_endpoint_events
    FROM {{ ref('int_asset_risk') }}
),

security_event_metrics AS (
    SELECT
        COUNT(*) AS total_security_events,
        SUM(is_suspicious) AS suspicious_events
    FROM {{ ref('int_security_events') }}
)

SELECT
    CURRENT_TIMESTAMP AS calculated_at,

    a.total_login_attempts,
    a.failed_login_attempts,

    ROUND(
        100.0 * a.failed_login_attempts
        / NULLIF(a.total_login_attempts, 0),
        2
    ) AS failed_login_rate_pct,

    p.privileged_activity_count,

    i.incident_volume,

    am.total_assets,
    am.high_criticality_assets,
    am.high_severity_endpoint_events,

    s.total_security_events,
    s.suspicious_events,

    ROUND(
        100.0 * s.suspicious_events
        / NULLIF(s.total_security_events, 0),
        2
    ) AS suspicious_event_rate_pct,

    CAST(NULL AS NUMERIC) AS mttr_hours

FROM authentication_metrics a
CROSS JOIN privileged_metrics p
CROSS JOIN incident_metrics i
CROSS JOIN asset_metrics am
CROSS JOIN security_event_metrics s