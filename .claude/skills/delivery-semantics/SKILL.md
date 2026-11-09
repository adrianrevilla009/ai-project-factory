---
name: delivery-semantics
description: Usar al decidir garantías de entrega (at-least-once, exactly-once efectivo), consumidores idempotentes y patrón outbox entre servicios.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Semánticas de entrega

## Cuándo aplicar y cuándo no
- Aplica a cualquier integración asíncrona (eventos, colas, webhooks) donde un mensaje puede perderse, duplicarse o llegar desordenado.
- No aplica a lecturas puras sin efectos laterales.

## Reglas
- **MUST** asumir **at-least-once** como base: todo consumidor recibe duplicados.
- **MUST** declarar por integración su garantía (at-most-once, at-least-once, efectivamente-una-vez) en el contrato (AsyncAPI / documento de diseño).
- **MUST** lograr "efectivamente una vez" con idempotencia en el receptor (tabla de eventos procesados con clave única `eventId`), no esperando exactly-once del transporte.
- **MUST** publicar eventos de dominio con el patrón **outbox transaccional** (fila en la misma transacción que el cambio de estado + relay); **MUST NOT** hacer doble escritura BD + broker sin outbox.
- **MUST NOT** depender del orden global; el orden solo se garantiza por clave de partición/grupo de mensajes.
- **MUST** que el consumidor registre el `eventId` y aplique el efecto en la misma transacción local.
- **SHOULD** incluir en cada evento `eventId` (UUID), `occurredAt` y versión del esquema.
- **SHOULD** usar transacciones Kafka (`read_committed`) solo para pipelines Kafka-a-Kafka; no cubren efectos en BD externas.
- **SHOULD** purgar la tabla de eventos procesados con una retención mayor que la ventana máxima de reentrega.

## Por qué
Las redes fallan entre "procesé" y "confirmé"; el broker reenvía. Exactly-once de extremo a extremo no existe sin cooperación del receptor. Sin outbox, un fallo entre el `commit` de la BD y el `send` deja el sistema inconsistente de forma irrecuperable. Verificar el alcance real de las transacciones Kafka en su documentación.

## Ejemplos
### Mal
```java
@Transactional
void placeOrder(Order o) {
    orderRepo.save(o);
    kafkaTemplate.send("orders.v1", o.id().toString(), toEvent(o)); // si falla tras commit: evento perdido
}
```
### Bien (outbox + consumidor idempotente)
```java
@Transactional
void placeOrder(Order o) {
    orderRepo.save(o);
    outboxRepo.save(new OutboxEntry(UUID.randomUUID(), "orders.v1",
        o.id().toString(), toJson(toEvent(o))));
}

@Transactional
void handle(OrderCreated e) {
    if (!processedRepo.insertIfAbsent(e.eventId())) { return; } // duplicado
    billing.charge(e);
}
```
```sql
CREATE TABLE processed_event (
    event_id UUID PRIMARY KEY,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- insertIfAbsent: INSERT ... ON CONFLICT (event_id) DO NOTHING
```

## Criterios de decisión y trampas
### Cómo decidir
- Asume entrega al menos una vez y haz idempotente el consumidor; «exactamente una vez» solo existe dentro de los límites de un sistema.
- Documenta qué garantiza cada canal.
### Trampas frecuentes
- Creer que una transacción del broker cubre efectos en otra base de datos.
- Consumidores que no toleran duplicados.
- Orden asumido entre particiones.
- Confirmar antes de procesar.
- Mezclar semánticas sin documentarlo.
### Evidencia
- Una prueba entrega el mismo mensaje dos veces y comprueba un único efecto.

## Checklist de revisión
- [ ] La garantía de entrega está declarada.
- [ ] Existe outbox para eventos de dominio; no hay doble escritura.
- [ ] El consumidor deduplica por `eventId` en la misma transacción.
- [ ] Ninguna lógica asume orden global.
- [ ] Hay prueba que entrega el mismo mensaje dos veces.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de entrega duplicada | 1 | tests del proyecto generado (pendiente) |
| Revisión de diseño de integración | 3 | agente `code-reviewer` / revisión humana |

> Estado: sin artefacto en este repositorio todavía (pendiente). Revisión humana del diseño.

## Relacionados, fuentes y mantenimiento
- Relacionados: `kafka-producers-consumers`, `idempotency-keys`, `dlq-retries-poison-messages`, `webhooks`.
- Fuentes: documentación de Apache Kafka (semántica de entrega, transacciones); patrón Transactional Outbox (microservices.io).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
