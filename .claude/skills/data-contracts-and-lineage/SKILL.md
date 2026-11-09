---
name: data-contracts-and-lineage
description: "Usar al acordar el esquema y SLAs de un dataset entre productor y consumidores (data contract) y al capturar linaje con OpenLineage/Marquez."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Data contracts y linaje

## Cuándo aplicar y cuándo no
- Aplica a datasets compartidos entre equipos o expuestos a BI/ML, y a pipelines que deben poder responder "de dónde viene este dato".
- No aplica a tablas internas efímeras de un solo job ni a contratos de API síncronas (ver `openapi-contract-first`, `asyncapi-event-contracts`).

## Reglas
- **MUST** versionar un contrato por dataset publicado: esquema (nombres, tipos, nulabilidad), semántica, propietario, frescura/SLA, clasificación de datos y política de retención.
- **MUST** guardar el contrato en el repositorio del productor (YAML) y validarlo en CI contra el esquema real.
- **MUST** tratar cambios incompatibles (borrar/renombrar/cambiar tipo) como versión mayor con periodo de convivencia.
- **MUST** validar datos contra el contrato en el pipeline (no solo el esquema: también reglas de calidad, ver `data-quality`).
- **MUST** emitir linaje por ejecución (job, run, datasets de entrada/salida) con OpenLineage desde orquestador y dbt/Spark.
- **MUST NOT** incluir valores de PII en los eventos de linaje ni en facets.
- **SHOULD** usar un estándar abierto para el contrato (Open Data Contract Standard u otro).
- **SHOULD** usar Marquez (OSS) como backend de linaje de referencia en local.

## Por qué
Sin contrato, un renombrado de columna aguas arriba rompe informes en silencio. El linaje acota el impacto de un cambio y apoya auditoría y RGPD. OpenLineage define Dataset, Job y Run, extensibles con facets, con integraciones para Airflow, dbt y Spark; Marquez es su implementación de referencia. Fuente: https://openlineage.io/docs/ (consultado 2026-11-07). Nombres de propiedades de configuración de cada integración.

## Ejemplos
### Mal
```text
"El esquema está en el wiki." (sin versión, sin dueño, sin validación)
```
### Bien
```yaml
# contracts/orders.v1.yaml  (formato propio ilustrativo; alinear con un estándar)
dataset: marts.fct_orders
version: 1.2.0
owner: team-sales
classification: internal
freshness: { max_age_hours: 2 }
retention_days: 1095
schema:
  - { name: order_id, type: string, nullable: false, unique: true }
  - { name: amount_eur, type: decimal(12,2), nullable: false }
  - { name: customer_email, type: string, pii: true, exposed: false }
```
```text
CI: compara contracts/orders.v1.yaml con el esquema real; falla si falta una columna o cambia un tipo sin subir major.
```

## Criterios de decisión y trampas
### Cómo decidir
- Un contrato entre productor y consumidor con esquema, semántica, frescura y propietario; el linaje muestra de dónde viene cada dato.
- Los cambios incompatibles requieren aviso y versión.
### Trampas frecuentes
- Consumir tablas internas del productor como contrato.
- Contratos sin validar automáticamente.
- Linaje dibujado a mano.
- Cambios sin aviso.
- Sin propietario del dato.
### Evidencia
- Un contrato validado en CI y un linaje generado automáticamente.

## Checklist de revisión
- [ ] Cada dataset publicado tiene contrato versionado con dueño y SLA.
- [ ] CI valida esquema real vs. contrato; cambios incompatibles suben versión mayor.
- [ ] Linaje emitido por orquestador y transformaciones, sin PII.
- [ ] Consumidores conocidos listados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validación contrato vs. esquema en CI | 1 | pendiente (proyecto generado) |
| Validador de esquemas de la fábrica (formato de artefactos) | 1 | `factory/validators/schemas_and_adrs.py` (no valida contratos de datos) |
| Revisión de cambios de contrato con consumidores | 3 | revisión humana |

Local: Marquez en contenedor. No se reproduce DataZone/Glue Data Catalog; preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-quality`, `data-governance-and-classification`, `asyncapi-event-contracts`, `cdc-and-streaming`.
- Fuentes: documentación OpenLineage (URL arriba, 2026-11-07).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
