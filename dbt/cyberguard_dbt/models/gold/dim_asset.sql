SELECT
    asset_id,
    owner,
    type,
    criticality
FROM {{ ref('stg_assets') }}