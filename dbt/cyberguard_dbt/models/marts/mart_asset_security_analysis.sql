WITH network_activity AS (

    SELECT
        asset_id,
        COUNT(*) AS network_event_count,
        COALESCE(SUM(bytes), 0) AS total_network_bytes
    FROM {{ ref('fact_network_activity') }}
    GROUP BY asset_id

),

endpoint_activity AS (

    SELECT
        asset_id,
        COUNT(*) AS endpoint_event_count,
        SUM(is_suspicious) AS suspicious_endpoint_event_count
    FROM {{ ref('fact_endpoint_events') }}
    GROUP BY asset_id

)

SELECT
    a.asset_id,
    a.owner,
    a.type,
    a.criticality,

    COALESCE(n.network_event_count, 0) AS network_event_count,
    COALESCE(n.total_network_bytes, 0) AS total_network_bytes,

    COALESCE(e.endpoint_event_count, 0) AS endpoint_event_count,
    COALESCE(e.suspicious_endpoint_event_count, 0)
        AS suspicious_endpoint_event_count,

    (
        COALESCE(n.network_event_count, 0)
        + COALESCE(e.endpoint_event_count, 0)
        + COALESCE(e.suspicious_endpoint_event_count, 0)
    ) AS activity_risk_indicator

FROM {{ ref('dim_asset') }} a

LEFT JOIN network_activity n
    ON a.asset_id = n.asset_id

LEFT JOIN endpoint_activity e
    ON a.asset_id = e.asset_id