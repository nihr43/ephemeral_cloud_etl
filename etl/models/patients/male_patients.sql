{{ config(materialized='table') }}

select distinct patid
from {{ source('public','patients') }}
where sex = 'M'
