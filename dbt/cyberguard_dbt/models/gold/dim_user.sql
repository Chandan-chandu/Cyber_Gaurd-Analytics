SELECT
    user_id,
    department,
    role,
    privilege_level
FROM {{ ref('stg_users') }}