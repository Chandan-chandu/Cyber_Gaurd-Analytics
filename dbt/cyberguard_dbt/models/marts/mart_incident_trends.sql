SELECT
    DATE_TRUNC('day', created_at) AS incident_date,
    severity,
    status,
    COUNT(*) AS incident_count
FROM {{ ref('int_incident_metrics') }}
GROUP BY
    DATE_TRUNC('day', created_at),
    severity,
    status
ORDER BY
    incident_date,
    severity,
    status