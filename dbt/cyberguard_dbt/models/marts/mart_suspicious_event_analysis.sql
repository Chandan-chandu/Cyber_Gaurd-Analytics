SELECT
    date_day,
    asset_id,
    process,
    severity,
    COUNT(*) AS suspicious_event_count

FROM {{ ref('fact_endpoint_events') }}

WHERE is_suspicious = 1

GROUP BY
    date_day,
    asset_id,
    process,
    severity

ORDER BY
    date_day,
    severity,
    asset_id