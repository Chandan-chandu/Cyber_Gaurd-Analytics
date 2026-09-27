SELECT
    asset_id,
    owner,
    type,
    criticality,
    network_event_count,
    endpoint_event_count,
    high_severity_endpoint_count,
    (
        network_event_count
        + endpoint_event_count
        + high_severity_endpoint_count
    ) AS activity_risk_indicator
FROM {{ ref('int_asset_risk') }}