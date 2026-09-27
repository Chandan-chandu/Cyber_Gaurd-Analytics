WITH authentication_metrics AS (

    SELECT
        COUNT(*) AS total_login_attempts,
        SUM(is_failed) AS failed_login_attempts
    FROM {{ ref('fact_authentication') }}

),

incident_metrics AS (

    SELECT
        COUNT(*) AS total_incidents,
        SUM(is_resolved) AS resolved_incidents
    FROM {{ ref('fact_incidents') }}

),

asset_metrics AS (

    SELECT
        COUNT(*) AS total_assets,
        COUNT(*) FILTER (
            WHERE UPPER(criticality) = 'HIGH'
        ) AS high_criticality_assets
    FROM {{ ref('dim_asset') }}

),

endpoint_metrics AS (

    SELECT
        COUNT(*) AS total_endpoint_events,
        SUM(is_suspicious) AS suspicious_endpoint_events
    FROM {{ ref('fact_endpoint_events') }}

),

network_metrics AS (

    SELECT
        COUNT(*) AS total_network_events,
        SUM(bytes) AS total_network_bytes
    FROM {{ ref('fact_network_activity') }}

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

    i.total_incidents,
    i.resolved_incidents,

    ROUND(
        100.0 * i.resolved_incidents
        / NULLIF(i.total_incidents, 0),
        2
    ) AS incident_resolution_rate_pct,

    am.total_assets,
    am.high_criticality_assets,

    e.total_endpoint_events,
    e.suspicious_endpoint_events,

    ROUND(
        100.0 * e.suspicious_endpoint_events
        / NULLIF(e.total_endpoint_events, 0),
        2
    ) AS suspicious_endpoint_rate_pct,

    n.total_network_events,
    n.total_network_bytes

FROM authentication_metrics a
CROSS JOIN incident_metrics i
CROSS JOIN asset_metrics am
CROSS JOIN endpoint_metrics e
CROSS JOIN network_metrics n