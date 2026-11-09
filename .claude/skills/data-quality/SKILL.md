---
name: data-quality
description: "Usar al definir o revisar controles de calidad de datos en pipelines: dimensiones de calidad, tests dbt/Great Expectations, umbrales, cuarentena y qué hacer cuando fallan."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Calidad de datos

## Cuándo aplicar y cuándo no
- Aplica a cualquier dataset que alimente informes, ML o integraciones.
- No aplica a validación de entrada de una API (ver `input-validation-output-encoding`) ni a monitorización continua de frescura/volumen (ver `data-observability`).

## Reglas
- **MUST** definir por dataset las dimensiones relevantes: unicidad, completitud, validez, integridad referencial, frescura, consistencia.
- **MUST** ejecutar tests en el pipeline, entre capas, y bloquear la publicación al mart si fallan los de severidad `error`.
- **MUST** distinguir severidad: `error` (bloquea) y `warn` (alerta); **MUST** documentar el umbral (p. ej. nulos < 0,5 %).
- **MUST** poner en cuarentena las filas inválidas (tabla `_rejects` con motivo), no descartarlas en silencio.
- **MUST** asignar un propietario por dataset que reciba las alertas.
- **MUST NOT** "arreglar" datos corruptos en el mart; corregir en origen o en una capa intermedia trazable.
- **SHOULD** empezar por PK única/no nula, FKs y valores aceptados (los cuatro tests genéricos de dbt) y añadir reglas de negocio después.
- **SHOULD** usar herramientas OSS (dbt tests; Great Expectations Core, comprobar licencia y versión vigentes).
- **SHOULD** versionar las expectativas junto al código del pipeline.

## Por qué
Un pipeline que "termina en verde" con datos erróneos es peor que uno que falla: el error llega a decisiones de negocio. dbt incluye de serie `unique`, `not_null`, `accepted_values` y `relationships`, declarados bajo `data_tests:` (https://docs.getdbt.com/docs/build/data-tests, consultado 2026-11-07). La cuarentena preserva evidencia y permite reprocesar.

## Ejemplos
### Mal
```sql
-- se filtran filas "malas" sin rastro
create table marts.fct_sales as select * from stg.sales where amount is not null and amount > 0;
```
### Bien
```sql
create table rejects.sales as
select s.*, case when amount is null then 'amount_null' else 'amount_non_positive' end as reason
from stg.sales s where amount is null or amount <= 0;
```
```yaml
models:
  - name: fct_sales
    columns:
      - name: sale_id
        data_tests: [unique, not_null]
      - name: status
        data_tests:
          - accepted_values:
              config: { severity: warn }
              arguments: { values: ['placed', 'shipped', 'returned'] }
```
Forma de `arguments`/`config` según la versión de dbt (comprobar al fijar la versión).

## Checklist de revisión
- [ ] Cada dataset tiene tests de PK, FKs y valores aceptados.
- [ ] Severidades y umbrales documentados; fallo `error` bloquea publicación.
- [ ] Filas rechazadas van a cuarentena con motivo.
- [ ] Hay propietario y canal de alerta.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `dbt test` bloqueante en CI/orquestador | 1 | pendiente (proyecto generado) |
| Semgrep: modelos sin fuente enumerada | 1 | `policies/semgrep/dbt-select-star-source.yaml` |
| Revisión de umbrales y propietarios | 3 | revisión humana (data owner) |

Local: dbt/Great Expectations sobre Postgres/DuckDB. Sin diferencias con AWS salvo el motor; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `etl-vs-elt-and-dbt`, `data-observability`, `data-contracts-and-lineage`, `batch-orchestration`.
- Fuentes: documentación dbt (URL arriba, 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
