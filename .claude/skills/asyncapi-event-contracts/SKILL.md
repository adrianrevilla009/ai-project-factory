---
name: asyncapi-event-contracts
description: "Usar al definir o cambiar eventos/mensajes asíncronos (Kafka, SQS, RabbitMQ): contrato AsyncAPI, envelope y naming."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Contratos de eventos con AsyncAPI

## Cuándo aplicar y cuándo no
- Aplica a todo servicio que publica o consume eventos o comandos por un broker.
- No aplica a llamadas síncronas (ver `openapi-contract-first`) ni a mensajes puramente internos de un único módulo.

## Reglas
- **MUST** documentar cada canal, mensaje y esquema en un documento AsyncAPI versionado junto al servicio productor (`src/main/resources/asyncapi/<service>.yaml`).
- **MUST** usar un envelope común con: `id` (UUID, único por evento), `type`, `source`, `time` (UTC), `specversion`/`schemaVersion` y `correlationId`; se recomienda alinear con CloudEvents.
- **MUST** nombrar eventos en pasado de dominio (`order.placed.v1`) y comandos en imperativo; **MUST NOT** nombrarlos por la tecnología.
- **MUST** definir la clave de partición/orden (p. ej. `orderId`) en el contrato.
- **MUST** publicar el esquema (JSON Schema/Avro/Protobuf) y validarlo en CI con compatibilidad (`schema-registry-and-evolution`, `backward-compatibility-rules`).
- **MUST NOT** incluir datos personales innecesarios ni secretos en el payload (`pii-and-data-classification`).
- **SHOULD** preferir eventos con estado suficiente para el consumidor (event-carried state) frente a "solo id", salvo coste justificado.
- **SHOULD** indicar semántica de entrega esperada y política de reintento/DLQ en la descripción del canal.

## Por qué
Sin contrato, el productor no sabe quién rompe al cambiar un campo, y los consumidores dependen de lo que ven en los logs. El envelope común habilita idempotencia, trazabilidad y enrutado uniformes.

## Ejemplos
### Mal
```java
kafka.send("orders", new ObjectMapper().writeValueAsString(orderEntity)); // sin versión ni id, entidad interna
```
### Bien
```yaml
asyncapi: 3.0.0
info: { title: Orders Events, version: 1.0.0 }
channels:
  orderPlaced:
    address: orders.order-placed.v1
    messages:
      OrderPlaced: { $ref: "#/components/messages/OrderPlaced" }
operations:
  publishOrderPlaced:
    action: send
    channel: { $ref: "#/channels/orderPlaced" }
components:
  messages:
    OrderPlaced:
      name: order.placed.v1
      payload: { $ref: "#/components/schemas/OrderPlacedPayload" }
```
```json
{ "id": "5b1c0f5e-0000-4000-8000-000000000001", "type": "order.placed.v1",
  "source": "orders-service", "time": "2026-11-07T10:00:00Z",
  "correlationId": "example-corr-1", "data": { "orderId": "o-1", "total": "10.50", "currency": "EUR" } }
```

## Checklist de revisión
- [ ] Canal y mensaje en AsyncAPI; esquema publicado.
- [ ] Envelope completo con `id` único y versión.
- [ ] Clave de partición definida.
- [ ] Cambio verificado como compatible.
- [ ] Sin PII innecesaria.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Validación AsyncAPI + chequeo de compatibilidad de esquema en CI | 1 | pendiente: pipeline del proyecto y ruleset en `policies/` |
| Revisión de contrato antes de publicar | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `schema-registry-and-evolution`, `kafka-producers-consumers`, `delivery-semantics`, `dlq-retries-poison-messages`, `backward-compatibility-rules`.
- Fuentes: asyncapi.com (especificación 3.0), cloudevents.io.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
