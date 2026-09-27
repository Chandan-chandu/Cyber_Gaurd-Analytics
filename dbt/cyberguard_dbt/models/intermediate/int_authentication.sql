SELECT
    a.event_id,
    a.user_id,
    u.department,
    u.role,
    u.privilege_level,
    a.timestamp,
    a.ip,
    a.action,
    a.result,
    a.location
FROM {{ ref('stg_auth_logs') }} a
LEFT JOIN {{ ref('stg_users') }} u
    ON a.user_id = u.user_id