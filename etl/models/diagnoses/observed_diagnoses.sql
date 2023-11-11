{{ config(materialized='table') }}

select distinct
  diag.dx_code,
  map.description
from {{ source('public','diagnoses') }} diag
join {{ source('public','icd10') }} map on diag.dx_code = map.dx_code
