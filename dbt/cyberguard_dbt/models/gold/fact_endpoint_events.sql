SELECT
    e.event_id,
    e.asset_id,
    DATE(e.timestamp) AS date_day,
    e.timestamp,
    e.process,
    e.severity,

    CASE
        WHEN UPPER(e.severity) IN ('HIGH', 'CRITICAL') THEN 1
        ELSE 0
    END AS is_suspicious

FROM {{ ref('stg_endpoint_events') }} e