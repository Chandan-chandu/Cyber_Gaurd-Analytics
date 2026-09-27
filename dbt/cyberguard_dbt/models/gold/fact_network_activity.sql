SELECT
    n.event_id,
    n.asset_id,
    DATE(n.timestamp) AS date_day,
    n.timestamp,
    n.source_ip,
    n.destination_ip,
    n.bytes
FROM {{ ref('stg_network_logs') }} n