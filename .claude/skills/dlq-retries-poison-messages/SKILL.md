---
name: dlq-retries-poison-messages
description: Usar al diseñar reintentos, dead-letter queues y manejo de mensajes venenosos en consumidores Kafka, RabbitMQ o SQS.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# DLQ, reintentos y mensajes venenosos

## Cuándo aplicar y cuándo no
- Aplica a todo consumidor asíncrono que pueda fallar al procesar un mensaje.
- No aplica a llamadas síncronas HTTP (usar resiliencia de cliente: timeouts, circuit breaker).

## Reglas
- **MUST** distinguir errores transitorios (red, timeout, 503: reintentar) de permanentes (validación, deserialización, regla de negocio: a DLQ sin reintentar).
- **MUST** limitar los reintentos y usar backoff exponencial con jitter; **MUST NOT** reintentar en bucle infinito ni sin espera.
- **MUST** enviar a una DLQ el mensaje que agota reintentos, conservando payload original, clave, cabeceras y motivo (excepción, intentos, topic/partición/offset de origen).
- **MUST** tener alerta sobre la profundidad/tasa de la DLQ y un runbook de reproceso.
- **MUST NOT** perder mensajes en silencio (`catch` que solo registra y confirma).
- **MUST** garantizar que reprocesar desde la DLQ es seguro (consumidor idempotente, ver `delivery-semantics`).
- **SHOULD** usar topics/colas de reintento por etapas solo si el bloqueo de la partición es inaceptable; si no, reintento en proceso con backoff corto.
- **SHOULD** contener PII fuera de los logs de la DLQ; tratar la DLQ con el mismo control de acceso y retención que la fuente.

## Por qué
Un mensaje venenoso reintentado sin límite bloquea una partición entera y propaga retraso a todo lo posterior. Un descarte silencioso pierde datos sin rastro. Una DLQ sin alerta es un cementerio. Las clases y propiedades de Spring Kafka, RabbitMQ y SQS deben contrastarse con su documentación vigente (TODO-VERIFY).

## Ejemplos
### Mal
```java
@KafkaListener(topics = "payments.v1")
void onPayment(PaymentEvent e) {
    try { service.apply(e); }
    catch (Exception ex) { log.error("failed", ex); } // se confirma y se pierde
}
```
### Bien (Spring Kafka)
```java
@Bean
DefaultErrorHandler errorHandler(KafkaTemplate<Object, Object> template) {
    var recoverer = new DeadLetterPublishingRecoverer(template,
        (rec, ex) -> new TopicPartition(rec.topic() + ".dlt", rec.partition()));
    var backoff = new ExponentialBackOffWithMaxRetries(4);
    backoff.setInitialInterval(500);
    backoff.setMultiplier(2.0);
    var handler = new DefaultErrorHandler(recoverer, backoff);
    handler.addNotRetryableExceptions(
        DeserializationException.class, ValidationException.class);
    return handler;
}
```
### Bien (SQS: redrive policy)
```json
{"deadLetterTargetArn":"arn:aws:sqs:eu-west-1:000000000000:payments-dlq",
 "maxReceiveCount":5}
```
ARN de ejemplo (`example`); la política es configuración preparada para AWS, no verificada en real. En local, LocalStack o ElasticMQ solo emulan la redrive de forma aproximada.

## Checklist de revisión
- [ ] Errores permanentes no se reintentan.
- [ ] Reintentos acotados con backoff y jitter.
- [ ] DLQ con contexto de origen, alerta y runbook.
- [ ] Ningún `catch` traga el mensaje.
- [ ] Reproceso desde DLQ probado con duplicados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de integración: mensaje venenoso termina en DLQ | 1 | tests del proyecto generado (pendiente) |
| Alerta de DLQ | 2 | reglas de alerta del proyecto generado (pendiente) |
| Revisión de manejo de errores | 3 | agente `code-reviewer` |

> Estado: sin artefacto en este repositorio todavía (pendiente).

## Relacionados, fuentes y mantenimiento
- Relacionados: `kafka-producers-consumers`, `rabbitmq-sqs`, `delivery-semantics`, `alerting-symptom-based`.
- Fuentes: documentación de Spring for Apache Kafka (manejo de errores y DLT) y de Amazon SQS (dead-letter queues), consultadas 2026-11-07 — TODO-VERIFY URLs y versión.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
