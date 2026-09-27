SELECT
    date_day,

    COUNT(*) AS total_login_attempts,

    SUM(is_failed) AS failed_login_attempts,

    COUNT(*) - SUM(is_failed) AS successful_login_attempts,

    ROUND(
        100.0 * SUM(is_failed)
        / NULLIF(COUNT(*), 0),
        2
    ) AS failed_login_rate_pct

FROM {{ ref('fact_authentication') }}

GROUP BY date_day

ORDER BY date_day