---
name: warehouse-options
description: "Usar al elegir el motor analítico/warehouse (PostgreSQL, ClickHouse, DuckDB, Trino, Redshift, Athena...) según volumen, concurrencia, latencia, coste y licencia."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Opciones de warehouse / motor analítico

## Cuándo aplicar y cuándo no
- Aplica al decidir dónde se consultan los marts y el histórico analítico.
- No aplica a elegir la BD transaccional (ver `datastore-selection-guide`) ni a almacenamiento de objetos del lago (ver `data-lake-and-lakehouse`).

## Reglas
- **MUST** decidir con un ADR que registre volumen (GB/TB), concurrencia de consultas, latencia objetivo, frescura, coste y licencia.
- **MUST** empezar por la opción más simple que cumpla: PostgreSQL (hasta cientos de GB, pocos usuarios) o DuckDB (analítica embebida, un nodo) antes de un clúster.
- **MUST** descartar por defecto soluciones con licencia de pago o cloud-only no justificadas (D16); registrar la excepción si se elige una.
- **MUST** mantener el SQL portable en marts (ANSI + dbt) para poder migrar de motor.
- **MUST NOT** ejecutar cargas analíticas pesadas contra la réplica/primaria transaccional sin aislamiento.
- **MUST NOT** copiar datos al warehouse y mantenerlos en paralelo con escritura desde la aplicación (4.5): una sola fuente de verdad, el warehouse se alimenta por carga/CDC.
- **SHOULD** separar almacenamiento y cómputo si la carga es variable (motor sobre Iceberg: Trino, Athena, Spark).
- **SHOULD** medir con una consulta representativa (benchmark propio) antes de decidir.

## Por qué
La elección por moda genera clústeres infrautilizados. Orientación general: PostgreSQL cubre analítica pequeña; ClickHouse (OSS) destaca en agregaciones sobre tablas anchas con alta ingesta; DuckDB, en análisis local/embebido; Trino, en consultas federadas sobre el lago; Redshift y Athena son servicios AWS gestionados con coste por uso. No se ha verificado aquí ninguna cifra de rendimiento ni precio.

## Ejemplos
### Mal
```text
Decisión: "Usamos Redshift porque es lo que hay en AWS."  (sin volumen, sin coste, sin alternativas)
```
### Bien
```markdown
# ADR-NNN Motor analítico para el mart de ventas
Contexto: 80 GB, 10 usuarios BI, refresco horario, presupuesto 0 licencias.
Opciones: PostgreSQL dedicado | ClickHouse | Athena sobre Iceberg.
Decisión: PostgreSQL dedicado con dbt; revisión al superar 500 GB o 50 usuarios.
Local: mismo motor. AWS: RDS/Aurora preparado, no verificado en real.
```
```sql
-- consulta de referencia para el benchmark propio
select date_trunc('month', sold_at) m, sum(amount) from marts.fct_sales group by 1;
```

## Checklist de revisión
- [ ] ADR con volumen, concurrencia, latencia, coste y licencia.
- [ ] Opción mínima evaluada primero; excepción de licencia justificada.
- [ ] Sin cargas analíticas sobre la BD transaccional.
- [ ] SQL de marts portable.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del ADR de motor analítico | 3 | revisión humana (data owner + arquitecto) |
| Validador de ADR (formato) | 1 | `factory/validators/schemas_and_adrs.py` |

Local: PostgreSQL, DuckDB, ClickHouse o Trino en contenedores. No se reproducen Redshift, Athena ni su facturación por uso; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `datastore-selection-guide`, `etl-vs-elt-and-dbt`, `data-platform-cost`, `bi-and-reporting`.
- Fuentes: pendientes comprobar (documentación oficial de cada motor).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
