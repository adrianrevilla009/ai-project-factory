---
name: consistency-and-sagas
description: "Usar al coordinar cambios que abarcan varios datastores o servicios (Postgres, DynamoDB, mensajería) y hay que elegir transacción local, saga o compensación."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Consistencia y sagas entre datastores

## Cuándo aplicar y cuándo no
- Aplica a flujos que modifican más de un datastore o servicio (p. ej. pedido en Postgres + reserva de stock en DynamoDB).
- No aplica a una operación dentro de un único datastore con transacción local. Detalle de orquestación/coreografía: `sagas-and-process-managers`; trade-offs generales: `consistency-and-cap-tradeoffs`.

## Reglas
- **MUST** preferir diseñar para que el invariante viva dentro de un solo aggregate/datastore (transacción local) antes de recurrir a una saga.
- **MUST NOT** usar dos escrituras directas a datastores distintos en un mismo método esperando atomicidad (sin doble escritura Postgres+NoSQL, 4.5); usar `outbox-and-cdc`.
- **MUST** que cada paso de la saga sea idempotente y tenga una compensación definida (o una justificación escrita de por qué no es compensable).
- **MUST** persistir el estado de la saga (id, paso actual, deadline) para sobrevivir a reinicios, y definir timeouts y estado terminal `FAILED`/`COMPENSATED`.
- **MUST** documentar la ventana de inconsistencia aceptada y qué ve el usuario durante ella.
- **SHOULD** usar transacciones nativas cuando el alcance es un solo almacén: DynamoDB `TransactWriteItems` agrupa hasta 100 acciones y 4 MB, en una región y cuenta; no son válidas entre regiones de una global table.
- **SHOULD** reintentar con `ClientRequestToken` en DynamoDB: es válido 10 minutos tras terminar la petición; pasado ese tiempo se trata como nueva.
- **MUST NOT** usar 2PC/XA entre almacenes heterogéneos como solución por defecto.

## Por qué
Entre datastores distintos no hay commit atómico. Las sagas lo sustituyen por pasos locales más compensaciones, aceptando estados intermedios visibles. Esa complejidad solo compensa si el negocio necesita realmente el reparto; por eso la primera regla es no repartir.

## Ejemplos
### Mal
```java
public void checkout(Cart c) {
    orderRepo.save(Order.from(c));        // Postgres
    stockTable.putItem(reserve(c));       // DynamoDB: si falla, pedido sin stock
}
```
### Bien
```java
@Transactional
public void checkout(Cart c) {
    var order = orderRepo.save(Order.pending(c));
    outbox.save(OutboxEvent.of("order", order.id(), "OrderPlaced", json(order)));
}
// StockService (idempotente por orderId) reserva y responde StockReserved | StockRejected.
// OrderSaga: StockReserved -> confirm(); StockRejected -> cancel() (compensacion); timeout 5 min -> cancel().
```

## Checklist de revisión
- [ ] Se intentó mantener el invariante en un solo aggregate/datastore.
- [ ] Cada paso es idempotente y tiene compensación o justificación.
- [ ] El estado de la saga se persiste y tiene timeout.
- [ ] Ventana de inconsistencia documentada.
- [ ] Sin escrituras duales directas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de flujos multi-datastore y de sus compensaciones | 3 | agente `code-reviewer` |
| Regla Semgrep contra dos escrituras a repositorios de datastores distintos en un método | pendiente | `policies/semgrep/` (no existe aún) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sagas-and-process-managers`, `outbox-and-cdc`, `idempotency-keys`, `consistency-and-cap-tradeoffs`, `transactions`.
- Fuentes (verificadas 2026-11-07): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
