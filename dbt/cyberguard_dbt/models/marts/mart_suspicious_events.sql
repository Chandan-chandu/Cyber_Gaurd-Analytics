SELECT
    event_id,
    asset_id,
    timestamp,
    process,
    severity,
    is_suspicious
FROM {{ ref('int_security_events') }}
WHERE is_suspicious = 1