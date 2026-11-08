---
name: etl-vs-elt-and-dbt
description: "Usar al elegir entre ETL y ELT y al modelar transformaciones SQL con dbt: capas staging/intermediate/marts, materializaciones incrementales, tests y documentación."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# ETL vs ELT y dbt

## Cuándo aplicar y cuándo no
- Aplica al decidir dónde se transforma el dato y al escribir modelos dbt (dbt Core, OSS).
- No aplica a transformaciones de negocio dentro de un microservicio ni a streaming con estado (ver `cdc-and-streaming`).

## Reglas
- **MUST** preferir ELT (cargar crudo, transformar en el motor analítico con SQL) cuando el destino escala; ETL solo si hay que filtrar/enmascarar antes de aterrizar (p. ej. PII, ver `gdpr-in-the-lake`).
- **MUST** conservar la capa raw inmutable; las transformaciones son reproducibles desde ella.
- **MUST** organizar modelos en capas: `staging` (1:1 con fuente, renombrado/tipado), `intermediate`, `marts` (consumo).
- **MUST** declarar tests en YAML para claves: `unique` y `not_null` en la PK, `relationships` en FKs, `accepted_values` en estados.
- **MUST** definir `unique_key` en modelos incrementales y filtrar con `is_incremental()`; **MUST** poder reconstruir con `--full-refresh`.
- **MUST NOT** usar `select *` desde `source()`; enumerar columnas.
- **MUST NOT** poner credenciales en `profiles.yml` versionado; usar variables de entorno.
- **SHOULD** documentar modelos y columnas (`description`) y exponer solo marts a BI.
- **SHOULD** usar dbt Core (OSS); dbt Cloud es de pago y requiere decisión explícita (D16).

## Por qué
ELT aprovecha el cómputo del warehouse y mantiene el crudo para recalcular; ETL se justifica por minimización de datos. Los incrementales sin `unique_key` duplican filas en reprocesos. Fuentes: https://docs.getdbt.com/docs/build/data-tests (4 tests genéricos, clave `data_tests`; desde v1.10.5 los argumentos van bajo `arguments:`) y https://docs.getdbt.com/docs/build/incremental-models (`unique_key`, `is_incremental()`, `on_schema_change`), consultadas 2026-11-07.

## Ejemplos
### Mal
```sql
-- models/marts/orders.sql
{{ config(materialized='incremental') }}
select * from {{ source('shop', 'orders') }}
```
### Bien
```sql
-- models/marts/fct_orders.sql
{{ config(materialized='incremental', unique_key='order_id', on_schema_change='fail') }}
select order_id, customer_id, status, ordered_at
from {{ ref('stg_shop__orders') }}
{% if is_incremental() %}
where ordered_at >= (select coalesce(max(ordered_at), '1900-01-01') from {{ this }})
{% endif %}
```
```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        data_tests: [unique, not_null]
      - name: customer_id
        data_tests:
          - relationships:
              arguments: { to: ref('dim_customers'), field: customer_id }
```
La forma `arguments:` depende de la versión de dbt (comprobar en la versión fijada).

## Checklist de revisión
- [ ] Capas respetadas; marts sin `source()` directo.
- [ ] Tests de PK/FK en cada modelo expuesto.
- [ ] Incrementales con `unique_key` y prueba de `--full-refresh`.
- [ ] Sin `select *` desde fuentes ni secretos versionados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: `select * from source()` | 1 | `policies/semgrep/dbt-select-star-source.yaml` |
| `dbt test` en CI | 1 | pendiente (pipeline del proyecto generado) |
| Revisión de modelo nuevo | 3 | revisión humana |

En local: dbt Core contra Postgres o DuckDB. No se reproducen Redshift/Athena/Glue; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-modeling`, `data-quality`, `warehouse-options`, `batch-orchestration`.
- Fuentes: documentación dbt (URLs arriba, 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
