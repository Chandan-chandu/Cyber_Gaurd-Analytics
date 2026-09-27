SELECT
    event_id,
    user_id,
    department,
    role,
    privilege_level,
    timestamp,
    ip,
    action,
    result,
    location
FROM {{ ref('int_privileged_activity') }}
ORDER BY timestamp