WITH date_range AS (

    SELECT
        MIN(event_date)::date AS min_date,
        MAX(event_date)::date AS max_date
    FROM (
        SELECT DATE(timestamp) AS event_date
        FROM {{ ref('stg_auth_logs') }}

        UNION ALL

        SELECT DATE(timestamp) AS event_date
        FROM {{ ref('stg_network_logs') }}

        UNION ALL

        SELECT DATE(timestamp) AS event_date
        FROM {{ ref('stg_endpoint_events') }}

        UNION ALL

        SELECT DATE(created_at) AS event_date
        FROM {{ ref('stg_incidents') }}
    ) dates

),

date_series AS (

    SELECT
        generate_series(
            min_date,
            max_date,
            interval '1 day'
        )::date AS date_day
    FROM date_range

)

SELECT
    date_day,
    EXTRACT(YEAR FROM date_day)::integer AS year,
    EXTRACT(QUARTER FROM date_day)::integer AS quarter,
    EXTRACT(MONTH FROM date_day)::integer AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(DAY FROM date_day)::integer AS day,
    EXTRACT(ISODOW FROM date_day)::integer AS day_of_week,
    TO_CHAR(date_day, 'Day') AS day_name
FROM date_series
ORDER BY date_day