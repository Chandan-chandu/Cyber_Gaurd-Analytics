SELECT
    a.event_id,
    a.user_id,
    DATE(a.timestamp) AS date_day,
    a.timestamp,
    a.ip,
    a.action,
    a.result,
    a.location,

    CASE
        WHEN LOWER(a.result) = 'failed' THEN 1
        ELSE 0
    END AS is_failed

FROM {{ ref('stg_auth_logs') }} a