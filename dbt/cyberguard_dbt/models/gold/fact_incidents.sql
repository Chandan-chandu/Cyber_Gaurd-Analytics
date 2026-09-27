SELECT
    i.incident_id,
    DATE(i.created_at) AS date_day,
    i.created_at,
    i.severity,
    i.status,
    i.resolution,

    CASE
    WHEN UPPER(i.status) = 'CLOSED' THEN 1
    ELSE 0
END AS is_resolved

FROM {{ ref('stg_incidents') }} i