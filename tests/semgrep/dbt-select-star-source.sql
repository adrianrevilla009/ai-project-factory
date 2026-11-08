// ruleid: dbt-model-select-star-from-source
select * from {{ source('crm', 'customers') }}
// ok: dbt-model-select-star-from-source
select id, name from {{ source('crm', 'customers') }}
