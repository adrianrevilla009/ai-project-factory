---
name: notifications
description: "Usar al diseñar envío de notificaciones (email, SMS, push, in-app): plantillas, preferencias, reintentos, idempotencia y proveedores."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Notificaciones

## Cuándo aplicar y cuándo no
- Aplica a cualquier mensaje saliente al usuario: email, SMS, push, in-app, webhooks hacia terceros.
- No aplica a alertas operativas (observabilidad/alerting) ni a eventos internos entre servicios.

## Reglas
- **MUST** desacoplar el origen del envío: el caso de uso emite un evento (outbox, ver `outbox-and-cdc`) y un consumidor `notification-service` envía.
- **MUST** garantizar idempotencia con `notification_key` (evento + destinatario + canal) y restricción única; reintentos no duplican mensajes.
- **MUST** respetar preferencias y consentimiento por canal y propósito (`consent-and-dsar-management`); las transaccionales se distinguen de las de marketing.
- **MUST** reintentar con backoff y DLQ (`dlq-retries-poison-messages`); fallo del proveedor no bloquea la transacción de negocio.
- **MUST** usar plantillas versionadas con i18n (`i18n-and-localization`); sin concatenar texto en código.
- **MUST NOT** registrar en logs el cuerpo, teléfono o email completos (PII).
- **MUST NOT** incluir secretos o tokens de larga vida en enlaces; usar tokens de un solo uso con caducidad.
- **SHOULD** abstraer proveedores tras `NotificationChannelPort` (SMTP local con MailHog/Mailpit en dev; el proveedor real de AWS, p. ej. SES, no se emula localmente y queda TODO-VERIFY).

## Por qué
Enviar dentro de la transacción de negocio provoca mensajes de operaciones revertidas o pérdidas. Sin clave de idempotencia, un reintento envía dos veces. Sin preferencias hay riesgo legal (normativa de comunicaciones comerciales: borrador, confirmar con fuente oficial).

## Ejemplos
### Mal
```java
@Transactional
public void placeOrder(Order o) {
    repo.save(o);
    mailSender.send(buildMessage(o)); // dentro de la tx, sin idempotencia
}
```
### Bien
```java
@KafkaListener(topics = "order.placed")
public void on(OrderPlaced e) {
    var key = e.eventId() + ":" + e.customerId() + ":EMAIL";
    if (!sent.tryInsert(key)) return; // UNIQUE(notification_key)
    if (!prefs.allows(e.customerId(), Channel.EMAIL, Purpose.TRANSACTIONAL)) return;
    channel.send(templates.render("order-placed", e.locale(), e));
}
```

## Checklist de revisión
- [ ] Envío fuera de la transacción de negocio.
- [ ] Clave de idempotencia única.
- [ ] Preferencias y consentimiento comprobados.
- [ ] Reintentos con DLQ; sin PII en logs.
- [ ] Plantillas versionadas e i18n.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep de logging (PII/estructura) | 1 | `policies/semgrep/java-logging.yaml` |
| Semgrep de Kafka auto-commit | 1 | `policies/semgrep/kafka-auto-commit.yaml` |
| Regla contra `mailSender.send` en `@Transactional` | 1 | pendiente |
| Revisión de preferencias/consentimiento | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `outbox-and-cdc`, `idempotency-keys`, `dlq-retries-poison-messages`, `consent-and-dsar-management`, `i18n-and-localization`.
- Fuentes: documentación del proveedor elegido: TODO-VERIFY. Preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
