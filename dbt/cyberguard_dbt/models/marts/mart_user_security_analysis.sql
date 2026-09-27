WITH authentication_activity AS (

    SELECT
        user_id,
        COUNT(*) AS login_attempts,
        SUM(is_failed) AS failed_login_attempts
    FROM {{ ref('fact_authentication') }}
    GROUP BY user_id

),

privileged_activity AS (

    SELECT
        user_id,
        COUNT(*) AS privileged_activity_count
    FROM {{ ref('mart_privileged_activity') }}
    GROUP BY user_id

)

SELECT
    u.user_id,
    u.department,
    u.role,
    u.privilege_level,

    COALESCE(a.login_attempts, 0) AS login_attempts,
    COALESCE(a.failed_login_attempts, 0) AS failed_login_attempts,

    ROUND(
        100.0 * COALESCE(a.failed_login_attempts, 0)
        / NULLIF(COALESCE(a.login_attempts, 0), 0),
        2
    ) AS failed_login_rate_pct,

    COALESCE(p.privileged_activity_count, 0)
        AS privileged_activity_count

FROM {{ ref('dim_user') }} u

LEFT JOIN authentication_activity a
    ON u.user_id = a.user_id

LEFT JOIN privileged_activity p
    ON u.user_id = p.user_id