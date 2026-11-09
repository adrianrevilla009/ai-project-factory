---
name: when-to-use-and-when-not
description: "Usar para decidir si un agregado necesita event sourcing, outbox o solo un audit trail; subskill de event-sourcing con árbol de decisión."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# Cuándo usar (y cuándo no) event sourcing

## Cuándo aplicar y cuándo no
- Aplica antes de adoptar event sourcing en un agregado, o cuando alguien pide "guardar todos los eventos".
- No aplica una vez decidido (ver `aggregates-and-event-design`, `dynamodb-event-store`). Subskill de `event-sourcing`.

## Reglas
- **MUST** responder por escrito a "¿los eventos SON el negocio?" (saldos, pólizas, expedientes, pedidos con historia): si no, no hay event sourcing.
- **MUST** distinguir tres necesidades y elegir la más barata que la cubra:
  1. Publicar hechos a otros sistemas: outbox (estado en Postgres + evento en la misma transacción).
  2. Saber quién cambió qué y cuándo: audit trail inmutable (`audit-trail-without-event-sourcing`).
  3. Reconstruir el estado en cualquier instante y derivar vistas de la historia: event sourcing.
- **MUST** recordar que event sourcing NO es auditoría: no la sustituye ni es la forma barata de obtenerla.
- **MUST NOT** combinar outbox y event sourcing en el mismo agregado: en event sourcing el almacén de eventos es la fuente de verdad y se publica desde él.
- **MUST NOT** hacer doble escritura del agregado en Postgres y en el event store.
- **MUST** abrir un ADR con alternativas descartadas, plan de versionado, de proyecciones y de supresión de datos personales (`gdpr-and-immutable-events`).
- **SHOULD** aplicarlo solo a agregados concretos, no a todo el sistema.

## Por qué
Event sourcing da historia completa y viaje en el tiempo, pero cobra un peso permanente: versionado de esquemas, consistencia eventual en lecturas, reconstrucciones y derecho de supresión. Es caro de revertir. La mayoría de las necesidades de auditoría o integración se cubren con un audit trail o un outbox.

## Ejemplos
### Mal
```text
"Queremos event sourcing para tener auditoría y publicar a Kafka."
-> Se resuelve con audit trail + outbox; ES añadiría coste sin necesidad.
```
### Bien
```text
Agregado: LedgerAccount (saldos; regulación exige reconstruir saldo a cualquier fecha)
Necesidad 3 confirmada -> event sourcing en DynamoDB (fuente de verdad, publica desde Streams)
Agregado: Customer (datos maestros, cambios auditados) -> Postgres + audit trail
Agregado: Order (estado + notificar a otros) -> Postgres + outbox
```
```text
¿Eventos = negocio y se necesita reconstruir en el tiempo?  si -> event sourcing
¿Solo notificar a otros sistemas de un cambio de estado?    si -> outbox
¿Solo trazabilidad de cambios?                              si -> audit trail
```

## Checklist de revisión
- [ ] ADR con respuesta a las tres necesidades.
- [ ] Alternativas (audit trail, outbox) descartadas con motivo.
- [ ] Alcance limitado a los agregados que lo requieren.
- [ ] Estrategia de versionado, proyecciones y supresión definida.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del ADR en el gate de arquitectura | 4 | `gates/` |
| Revisión de código: coexistencia de tabla de estado y event store para el mismo agregado | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `outbox-and-cdc`, `audit-trail-without-event-sourcing`, `cqrs`, `datastore-selection-guide`.
- Decisiones: ADR-0014; brief 4.5.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
