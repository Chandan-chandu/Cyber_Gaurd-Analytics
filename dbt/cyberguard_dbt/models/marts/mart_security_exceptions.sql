WITH user_exceptions AS (

    SELECT
        'USER'::TEXT AS exception_type,
        user_id::TEXT AS entity_id,
        department::TEXT AS department,
        role::TEXT AS role,
        privilege_level::TEXT AS privilege_level,
        failed_login_attempts::BIGINT AS event_count,
        failed_login_rate_pct::NUMERIC AS exception_rate,
        'HIGH_FAILED_LOGIN_RATE'::TEXT AS exception_reason

    FROM {{ ref('mart_user_security_analysis') }}

    WHERE failed_login_rate_pct >= 20

),

asset_exceptions AS (

    SELECT
        'ASSET'::TEXT AS exception_type,
        asset_id::TEXT AS entity_id,
        NULL::TEXT AS department,
        type::TEXT AS role,
        criticality::TEXT AS privilege_level,
        suspicious_endpoint_event_count::BIGINT AS event_count,
        NULL::NUMERIC AS exception_rate,
        'SUSPICIOUS_ENDPOINT_ACTIVITY'::TEXT AS exception_reason

    FROM {{ ref('mart_asset_security_analysis') }}

    WHERE suspicious_endpoint_event_count > 0

)

SELECT *
FROM user_exceptions

UNION ALL

SELECT *
FROM asset_exceptions