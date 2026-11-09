---
name: outbox-and-cdc
description: "Usar al publicar eventos tras un cambio en la base de datos sin doble escritura: patrón transactional outbox, relay por polling o CDC (Debezium, DynamoDB Streams)."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Outbox y CDC

## Cuándo aplicar y cuándo no
- Aplica cuando un cambio de estado debe producir un mensaje (Kafka, SQS) con garantía de que ambos ocurren o ninguno.
- No aplica si el mensaje no es crítico y se tolera perderlo, ni a lecturas. No sustituye a `idempotency-and-deduplication` en el consumidor.

## Reglas
- **MUST** escribir el cambio de estado y la fila `outbox` en la misma transacción local; NUNCA estado en la BD y publicar al broker en el mismo método sin outbox (doble escritura).
- **MUST** que el relay (polling o CDC) entregue al-menos-una-vez; los consumidores MUST ser idempotentes usando el `id` del evento.
- **MUST** que cada fila outbox lleve `id`, `aggregate_type`, `aggregate_id`, `type`, `payload`, `created_at`; la clave del mensaje es `aggregate_id` para conservar orden por aggregate.
- **MUST** purgar o archivar filas procesadas (retención definida); el outbox es una cola, no un histórico.
- **SHOULD** preferir CDC (Debezium `EventRouter`) cuando el volumen o la latencia penalizan el polling; polling con `SELECT ... FOR UPDATE SKIP LOCKED` es suficiente para volúmenes bajos.
- **MUST NOT** asumir orden global entre aggregates; solo por clave.
- En DynamoDB: **MUST** escribir ítem de estado y de outbox con `TransactWriteItems` (hasta 100 acciones y 4 MB) y relevar con DynamoDB Streams, que retiene 24 h: el relay debe estar operativo dentro de esa ventana o se pierden eventos.
- **MUST NOT** asumir que los registros de Streams de una misma transacción llegan juntos ni en orden entre ítems; solo hay orden por ítem.

## Por qué
Sin outbox, un fallo entre el commit y el envío deja el sistema inconsistente (estado cambiado, evento perdido) o publica eventos de cambios que luego hacen rollback. El outbox convierte el problema de consistencia distribuida en uno local más entrega at-least-once.

## Ejemplos
### Mal
```java
@Transactional
public void place(Order o) {
    orders.save(o);
    kafka.send("orders", o.id(), json(o)); // si commit falla, el evento ya salio
}
```
### Bien
```java
@Transactional
public void place(Order o) {
    orders.save(o);
    outbox.save(new OutboxEvent(UUID.randomUUID(), "order", o.id(), "OrderPlaced", json(o)));
}
```
```sql
create table outbox (
  id uuid primary key, aggregate_type text not null, aggregate_id text not null,
  type text not null, payload jsonb not null, created_at timestamptz not null default now()
);
```
Con Debezium el `EventRouter` lee por defecto las columnas `id`, `aggregatetype`, `aggregateid`, `payload` (nombres configurables; en el esquema de arriba habría que mapear los nombres con snake_case) y filtra los `DELETE` del outbox.

## Criterios de decisión y trampas
### Cómo decidir
- Escribe el evento en la misma transacción que el cambio de estado y publícalo después con un proceso fiable (sondeo o captura de cambios); así evitas la escritura doble.
- El consumidor debe ser idempotente.
### Trampas frecuentes
- Publicar al broker dentro de la transacción de negocio.
- Un outbox que crece sin limpieza.
- Sin orden por agregado.
- Un publicador único sin recuperación.
- Captura de cambios sin gestionar el esquema de los eventos.
### Evidencia
- Una prueba mata el publicador a mitad y comprueba que no se pierden ni duplican efectos.

## Checklist de revisión
- [ ] Estado y outbox en la misma transacción.
- [ ] Consumidores idempotentes por `id` de evento.
- [ ] Retención/purga del outbox definida.
- [ ] Clave de mensaje = aggregate id.
- [ ] Alerta por lag del relay (y por antigüedad de la fila más vieja).

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión: ningún `kafkaTemplate.send` dentro de servicios `@Transactional` de dominio | 3 | agente `code-reviewer` |
| Regla Semgrep para `send(` en métodos `@Transactional` | pendiente | `policies/semgrep/` (no existe aún) |
| Política de consumidores con auto-commit desactivado | 1 | `policies/semgrep/kafka-auto-commit.yaml` |

No se reproduce en local: la semántica de Streams y su retención de 24 h solo se emula parcialmente (ver `local-vs-aws-dynamodb-testing`).

## Relacionados, fuentes y mantenimiento
- Relacionados: `idempotency-and-deduplication`, `delivery-semantics`, `domain-events-in-spring`, `kafka-producers-consumers`, `consistency-and-sagas`.
- Fuentes (verificadas 2026-11-07): Debezium Outbox Event Router https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html · DynamoDB Streams https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.html · Transacciones https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
