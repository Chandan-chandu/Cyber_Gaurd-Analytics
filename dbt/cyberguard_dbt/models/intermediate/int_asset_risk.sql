SELECT
    a.asset_id,
    a.owner,
    a.type,
    a.criticality,
    COUNT(DISTINCT n.event_id) AS network_event_count,
    COUNT(DISTINCT e.event_id) AS endpoint_event_count,
    COUNT(DISTINCT CASE
        WHEN e.severity = 'HIGH' THEN e.event_id
    END) AS high_severity_endpoint_count
FROM {{ ref('stg_assets') }} a
LEFT JOIN {{ ref('stg_network_logs') }} n
    ON a.asset_id = n.asset_id
LEFT JOIN {{ ref('stg_endpoint_events') }} e
    ON a.asset_id = e.asset_id
GROUP BY
    a.asset_id,
    a.owner,
    a.type,
    a.criticality