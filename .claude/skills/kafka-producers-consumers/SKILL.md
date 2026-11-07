---
name: kafka-producers-consumers
description: Usar al escribir o revisar productores y consumidores Kafka con Spring Kafka (acks, idempotencia, commits de offsets, claves, concurrencia).
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Productores y consumidores Kafka

## Cuándo aplicar y cuándo no
- Aplica a cualquier servicio Java/Spring Boot que publique o consuma topics Kafka.
- No aplica a colas punto a punto (ver `rabbitmq-sqs`) ni al diseño del esquema del mensaje (ver `schema-registry-and-evolution`).

## Reglas
- **MUST** configurar el productor con `acks=all` y `enable.idempotence=true`.
- **MUST** fijar `delivery.timeout.ms` explícito y tratar el fallo del `send` (callback / `CompletableFuture`), nunca ignorarlo.
- **MUST** usar una clave de partición con significado de negocio (p. ej. `orderId`) cuando importe el orden por entidad.
- **MUST** desactivar el auto-commit del consumidor (`enable.auto.commit=false`) y confirmar offsets solo tras procesar con éxito.
- **MUST** hacer el procesamiento idempotente (ver `delivery-semantics`): el consumidor recibirá duplicados.
- **MUST** configurar `ErrorHandlingDeserializer` para que un mensaje corrupto no bloquee la partición.
- **MUST** definir `group.id` explícito por servicio; **MUST NOT** compartirlo entre aplicaciones distintas.
- **MUST NOT** hacer llamadas bloqueantes largas dentro del listener que superen `max.poll.interval.ms`.
- **SHOULD** dimensionar `concurrency` <= nº de particiones del topic.
- **SHOULD** usar el patrón outbox (no doble escritura BD + Kafka) para publicar eventos de dominio.
- **SHOULD** cabeceras estándar: `eventId`, `eventType`, `traceparent`.

## Por qué
Con `acks=1` un fallo de líder pierde mensajes ya "confirmados". Con auto-commit, el offset avanza antes de terminar el trabajo y un fallo pierde el mensaje en silencio. Un mensaje no deserializable sin manejador provoca un bucle infinito en la misma partición. Los nombres y valores por defecto de propiedades deben contrastarse con la documentación vigente de Kafka y Spring Kafka (TODO-VERIFY versión).

## Ejemplos
### Mal
```yaml
spring:
  kafka:
    producer:
      acks: 1
    consumer:
      enable-auto-commit: true
      group-id: app
```
```java
kafkaTemplate.send("orders", order); // sin clave, sin gestionar el resultado
```
### Bien
```yaml
spring:
  kafka:
    producer:
      acks: all
      properties:
        enable.idempotence: true
        delivery.timeout.ms: 120000
    consumer:
      group-id: billing-service
      enable-auto-commit: false
      properties:
        isolation.level: read_committed
    listener:
      ack-mode: record
```
```java
kafkaTemplate.send("orders.v1", order.id().toString(), event)
    .whenComplete((result, ex) -> {
        if (ex != null) { log.error("publish failed eventId={}", event.id(), ex); }
    });

@KafkaListener(topics = "orders.v1", groupId = "billing-service")
void onOrder(OrderCreated event) {
    processedEvents.runOnce(event.id(), () -> billing.charge(event)); // idempotente
}
```

## Checklist de revisión
- [ ] `acks=all` e idempotencia activos; resultado del `send` gestionado.
- [ ] Auto-commit desactivado; `group.id` propio del servicio.
- [ ] `ErrorHandlingDeserializer` y política de errores definidos (ver `dlq-retries-poison-messages`).
- [ ] Consumidor idempotente con prueba de duplicado.
- [ ] Clave de partición justificada; concurrencia <= particiones.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `enable-auto-commit: true` / `enable.auto.commit=true` | 1 | `policies/semgrep/kafka-auto-commit.yaml` |
| Test de duplicado en el proyecto generado | 1 | tests del proyecto generado (pendiente) |
| Revisión de configuración Kafka | 3 | agente `code-reviewer` |

> Estado: la regla Semgrep existe pero no se ha ejecutado (TODO-VERIFY). En local se usa un broker Kafka OSS; no se reproducen ACLs ni cifrado de un clúster gestionado.

## Relacionados, fuentes y mantenimiento
- Relacionados: `delivery-semantics`, `dlq-retries-poison-messages`, `schema-registry-and-evolution`, `asyncapi-event-contracts`.
- Fuentes: documentación de Apache Kafka (configuración de producer/consumer) y de Spring for Apache Kafka, consultar 2026-11-07 — TODO-VERIFY URLs y versión.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
