{{ config(materialized='table') }}

select distinct
  diag.provider as npi,
  pro.lname,
  pro.fname
from {{ source('public','diagnoses') }} diag
join {{ source('public','providers') }} pro on diag.provider = pro.npi
where pro.lname is not null
and pro.fname is not null
