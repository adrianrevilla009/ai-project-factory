---
name: rabbitmq-sqs
description: Usar al elegir o configurar colas RabbitMQ o Amazon SQS (acks, visibility timeout, DLQ, FIFO) y su equivalente local.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# RabbitMQ y SQS

## Cuándo aplicar y cuándo no
- Aplica a colas de trabajo / comandos asíncronos con RabbitMQ (local, OSS) o SQS (AWS).
- No aplica a log de eventos reproducible con múltiples grupos de consumidores (usar Kafka, ver `kafka-producers-consumers`).

## Reglas
- **MUST** elegir cola cuando el mensaje es una tarea para un consumidor; Kafka cuando es un hecho que varios lectores reproducen.
- **MUST** acks manuales en RabbitMQ (`acknowledge-mode: manual` o `auto` de Spring con excepciones bien tratadas) y `prefetch` acotado.
- **MUST** colas **quorum** en RabbitMQ para datos que no se pueden perder, con publisher confirms y mensajes `persistent`.
- **MUST** en SQS fijar `VisibilityTimeout` > tiempo máximo de proceso, `ReceiveMessageWaitTimeSeconds` (long polling) y una redrive policy con DLQ (ver `dlq-retries-poison-messages`).
- **MUST** borrar el mensaje SQS solo tras procesar con éxito.
- **MUST** consumidores idempotentes: SQS estándar es at-least-once y sin orden estricto; RabbitMQ reentrega tras desconexión.
- **SHOULD** SQS FIFO solo si se necesita orden/deduplicación; usar `MessageGroupId` con cardinalidad suficiente.
- **SHOULD** cifrado en reposo (SSE) y política de cola con mínimo privilegio en SQS.
- **MUST NOT** enviar payloads grandes por cola; guardar el objeto aparte y enviar la referencia. Tamaño máximo de mensaje en SQS: 1 MiB (1.048.576 bytes; verificado el 2026-11-08); para más, la Extended Client Library guarda el payload en S3 y envía la referencia.

## Por qué
Un `ack` previo al proceso pierde trabajo; un visibility timeout corto provoca procesamiento doble concurrente; una cola sin DLQ acumula mensajes venenosos eternamente. RabbitMQ y SQS tienen modelos distintos: no asumir equivalencia 1:1.

## Matriz AWS y local
- Local: RabbitMQ OSS, y ElasticMQ para SQS (LocalStack ya no tiene edición Community gratuita para uso comercial; ver `aws-emulation`).
- Preparado para AWS, no verificado en real. **No se reproduce en local:** IAM/políticas de cola reales, cifrado KMS, límites de cuota y throughput reales de FIFO, métricas CloudWatch.

## Ejemplos
### Mal
```java
@RabbitListener(queues = "invoices")
void handle(Invoice i) {
    channel.basicAck(tag, false); // ack antes de procesar
    service.process(i);
}
```
### Bien
```java
@SqsListener(value = "invoices", acknowledgementMode = "ON_SUCCESS")
void handle(InvoiceMessage m) {
    processed.runOnce(m.messageId(), () -> service.process(m)); // borra al terminar sin error
}
```
```hcl
resource "aws_sqs_queue" "invoices" {
  name                       = "invoices"
  visibility_timeout_seconds = 120
  receive_wait_time_seconds  = 20
  sqs_managed_sse_enabled    = true
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.invoices_dlq.arn
    maxReceiveCount     = 5
  })
}
```
Nombres de atributos Terraform: los recursos y sus argumentos de primer nivel se contrastaron con la documentación del provider AWS el 2026-11-08.

## Checklist de revisión
- [ ] Justificada cola frente a Kafka.
- [ ] Ack/delete solo tras éxito; prefetch o visibility timeout dimensionados.
- [ ] DLQ y redrive configurados; consumidor idempotente.
- [ ] Payload pequeño; cifrado y privilegio mínimo en SQS.
- [ ] Documentado qué no se reproduce en local.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Checkov: SQS sin cifrado / sin DLQ | 1 | `policies/iac-checks/` (pendiente) |
| Revisión de configuración de colas | 3 | agente `code-reviewer` |

> Estado: artefactos pendientes; revisión humana mientras tanto.

## Relacionados, fuentes y mantenimiento
- Relacionados: `dlq-retries-poison-messages`, `delivery-semantics`, `kafka-producers-consumers`.
- Fuentes: documentación de RabbitMQ (quorum queues, confirms, consumer acks) y de Amazon SQS (visibility timeout, DLQ, FIFO).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
