SELECT
    event_id,
    asset_id,
    timestamp,
    process,
    severity,
    CASE
        WHEN severity IN ('HIGH', 'CRITICAL') THEN 1
        ELSE 0
    END AS is_suspicious
FROM {{ ref('stg_endpoint_events') }}