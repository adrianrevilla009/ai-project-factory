---
name: dynamodb-event-store
description: "Usar al implementar un event store sobre DynamoDB: esquema de streams, append condicional, publicación desde DynamoDB Streams y límites."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Event store sobre DynamoDB

## Cuándo aplicar y cuándo no
- Aplica cuando `when-to-use-and-when-not` ya decidió event sourcing y el almacén es DynamoDB (ADR-0013, ADR-0014).
- No aplica a publicar eventos de integración desde un estado en Postgres (usar `outbox-and-cdc`) ni a auditoría (`audit-trail-without-event-sourcing`).

## Reglas
- **MUST** modelar un stream por agregado: `pk = <TYPE>#<aggregateId>`, `sk` = versión con ceros a la izquierda (`v0000000042`) para ordenar lexicográficamente.
- **MUST** añadir con escritura condicional `attribute_not_exists(pk)` sobre la clave completa `(pk, sk)`: dos escritores con la misma versión esperada, uno falla (concurrencia optimista).
- **MUST** escribir varios eventos del mismo comando en un solo `TransactWriteItems` (misma tabla, misma región) y respetar sus límites (TODO-VERIFY en la guía de la API).
- **MUST** publicar desde el propio almacén con DynamoDB Streams (o equivalente); **MUST NOT** publicar en el bus como segundo paso del comando (doble escritura).
- **MUST** tratar los consumidores como at-least-once: idempotentes por `(streamId, version)` (`idempotency-and-deduplication`).
- **MUST NOT** actualizar ni borrar ítems de eventos; la política IAM de la aplicación solo permite `PutItem` condicional y `Query`.
- **SHOULD** guardar metadatos: `type`, `schemaVersion`, `occurredAt`, `correlationId`, `causationId`, `payload`.
- **SHOULD** configurar retención y orden de Streams según la documentación vigente (TODO-VERIFY: retención de 24 h de los registros de Streams).
- **MUST** fijar la región de escritura por agregado si hay Global Tables (`global-tables-and-write-region-rules`).

## Por qué
La clave `(pk, sk)` convierte la versión en un candado: el append condicional da concurrencia optimista sin lectura previa. Publicar desde Streams evita que el evento se guarde pero no se emita (o al revés). Los registros de Streams son efímeros: el store es la fuente de verdad, así que se pueden republicar leyendo la tabla.

## Ejemplos
### Mal
```java
dynamo.putItem(PutItemRequest.builder().tableName("events").item(item).build()); // pisa versión existente
eventBus.publish(event);                                                         // segunda escritura
```
### Bien
```java
var put = Put.builder()
    .tableName("events")
    .item(Map.of(
        "pk", s("ORDER#" + orderId),
        "sk", s(String.format("v%010d", expectedVersion + 1)),
        "type", s("OrderPlaced"), "schemaVersion", n("2"),
        "payload", s(json), "occurredAt", s(Instant.now().toString())))
    .conditionExpression("attribute_not_exists(pk)")   // evalúa sobre (pk, sk)
    .build();
try {
    dynamo.transactWriteItems(b -> b.transactItems(TransactWriteItem.builder().put(put).build()));
} catch (TransactionCanceledException e) {
    throw new ConcurrencyConflictException(orderId, expectedVersion);
}
// La publicación la hace un consumidor de DynamoDB Streams, idempotente por pk+sk.
```

## Checklist de revisión
- [ ] Clave `(pk, sk=versión)` y append condicional.
- [ ] Ningún `UpdateItem`/`DeleteItem` sobre eventos; IAM lo impide.
- [ ] Publicación desde Streams, consumidores idempotentes.
- [ ] Esquema con `schemaVersion` y correlación.
- [ ] Región de escritura por agregado documentada si hay réplicas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `PutItemRequest` sin `conditionExpression` (heurística) | 1 | `policies/semgrep/dynamodb-put-without-condition.yaml` |
| Test de concurrencia (dos appends con misma versión) contra DynamoDB Local | 1 | tests del proyecto generado (`local-vs-aws-dynamodb-testing`) |
| Revisión de políticas IAM (sin update/delete) | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `aggregates-and-event-design`, `snapshots`, `projections-and-read-models`, `dynamodb-data-modeling`, `delivery-semantics`.
- Fuentes: documentación de DynamoDB Streams y de transacciones (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/) — límites y retención (por nombre; URL y versión se fijan al adoptarlas en el proyecto). Preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
