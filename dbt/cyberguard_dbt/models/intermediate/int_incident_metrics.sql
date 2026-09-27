SELECT
    incident_id,
    created_at,
    severity,
    status,
    resolution,
    CASE
        WHEN status = 'Resolved' THEN 1
        ELSE 0
    END AS is_resolved
FROM {{ ref('stg_incidents') }}