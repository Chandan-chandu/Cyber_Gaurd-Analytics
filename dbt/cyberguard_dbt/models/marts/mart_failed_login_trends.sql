SELECT
    DATE_TRUNC('day', timestamp) AS event_date,
    COUNT(*) AS total_login_attempts,
    COUNT(*) FILTER (
        WHERE LOWER(result) = 'failed'
    ) AS failed_login_attempts,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE LOWER(result) = 'failed'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS failed_login_rate_pct
FROM {{ ref('int_authentication') }}
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY event_date