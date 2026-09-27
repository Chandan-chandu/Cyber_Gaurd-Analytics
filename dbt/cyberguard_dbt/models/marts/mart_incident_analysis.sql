SELECT
    date_day,
    severity,
    status,

    COUNT(*) AS incident_count,

    SUM(
        CASE
            WHEN UPPER(status) = 'CLOSED' THEN 1
            ELSE 0
        END
    ) AS closed_incident_count

FROM {{ ref('fact_incidents') }}

GROUP BY
    date_day,
    severity,
    status

ORDER BY
    date_day,
    severity,
    status