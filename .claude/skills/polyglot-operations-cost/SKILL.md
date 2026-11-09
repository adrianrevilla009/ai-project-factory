---
name: polyglot-operations-cost
description: "Usar antes de añadir un almacén (DynamoDB, OpenSearch, Redis) a un proyecto, para estimar y aceptar su coste operativo y de equipo."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# Coste operativo de la persistencia políglota

## Cuándo aplicar y cuándo no
- Aplica en la propuesta de cualquier almacén adicional a Postgres y en la revisión anual de los existentes.
- No aplica a comparar tamaños de instancia dentro de un mismo almacén (ver `cost-visibility`).

## Reglas
- **MUST** rellenar una ficha de coste por almacén extra antes de aprobar su uso (tabla del ejemplo).
- **MUST** incluir en la ficha: backup y restauración probados, migraciones/evolución de esquema, observabilidad, alertas, seguridad (cifrado, IAM), runbook y propietario.
- **MUST** incluir un informe de coste estimado sin desplegar (Infracost o equivalente sobre el plan, ver brief 4.6); es una estimación, no una medición.
- **MUST** definir cómo se reconstruye cada almacén derivado (OpenSearch, Redis) desde la fuente de verdad.
- **SHOULD** limitar el proyecto a un máximo de dos almacenes persistentes de verdad salvo ADR explícito.
- **SHOULD** reservar capacidad de formación del equipo en la ficha: modelado DynamoDB o relevancia en OpenSearch no se improvisan.
- **MUST NOT** aprobar un almacén sin dueño de guardia ni procedimiento de recuperación.

## Por qué
El coste real de un almacén extra no es la factura mensual sino el trabajo continuo: parches, capacidad, incidentes, pruebas de restauración y conocimiento repartido. En local además se emula solo parcialmente (ver `local-vs-aws-dynamodb-testing`), lo que añade riesgo de integración. La ficha obliga a hacer visible ese coste antes de comprometerse (ADR-0013 lo declara como consecuencia asumida).

## Ejemplos
### Mal
```text
Propuesta: "añadimos OpenSearch porque el listado va lento"
(sin medir la consulta, sin índice en Postgres probado, sin dueño, sin plan de reindexado)
```
### Bien
```yaml
# docs/data/datastore-cost-card-opensearch.yaml
datastore: opensearch
reason: "búsqueda por texto y facetas sobre 20M documentos; Postgres tsvector medido: p95 4 s"
source_of_truth: postgres.orders
rebuild: "replay del outbox/CDC + reindex; tiempo estimado 3 h"
backup_restore_tested: pendiente          # no se marca true sin prueba real
monitoring: [cluster_health, indexing_lag, jvm_pressure]
owner: team-search
cost_estimate: "informe Infracost adjunto (estimación, no desplegado)"
team_training: "2 sesiones + guía de relevancia"
decision_review_date: 2027-05-07
```

## Checklist de revisión
- [ ] Existe ficha de coste por cada almacén no-Postgres.
- [ ] Hay dueño, runbook y plan de restauración.
- [ ] El almacén derivado se puede reconstruir y se sabe cuánto tarda.
- [ ] Hay estimación de coste (sin desplegar) y fecha de revisión.
- [ ] Se descartó antes una alternativa dentro de Postgres.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana de la ficha en el gate de arquitectura | 4 | `gates/` |
| Esquema JSON de la ficha validado en CI | 1 | pendiente (no existe todavía) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `datastore-selection-guide`, `cost-visibility`, `cqrs-read-models-and-search`, `cache-strategies`, `local-vs-aws-dynamodb-testing`.
- Decisiones: ADR-0013; brief 4.5 y 4.6.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
