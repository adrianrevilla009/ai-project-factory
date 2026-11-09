---
name: event-driven
description: "Usar al diseñar comunicación asíncrona por eventos o mensajes entre módulos o servicios: contratos, outbox, idempotencia y entrega."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Arquitectura dirigida por eventos

## Cuándo aplicar y cuándo no
- Aplica al desacoplar contexts, notificar hechos de negocio a varios consumidores o absorber picos con colas.
- No aplica cuando el llamador necesita respuesta inmediata y consistente (usar API síncrona) ni para "enviar comandos disfrazados de eventos".

## Reglas
- **MUST** distinguir evento (hecho pasado, `OrderPlaced`) de comando (petición, `ReserveStock`); el evento no espera respuesta.
- **MUST** publicar mediante outbox transaccional: el cambio de estado y el evento se guardan en la misma transacción; un relay los envía. Sin dual write a la BD y al broker.
- **MUST** asumir entrega al-menos-una-vez: consumidores idempotentes (tabla de mensajes procesados o upsert natural).
- **MUST** versionar y documentar el contrato del evento (esquema, campos obligatorios); cambios compatibles hacia atrás.
- **MUST** configurar reintentos con backoff y una dead-letter queue con alerta.
- **MUST NOT** asumir orden global; solo se garantiza dentro de una clave/partición.
- **MUST NOT** incluir en el evento el modelo interno completo; publicar lo que el consumidor necesita (o un id para consultar).
- **SHOULD** incluir `eventId`, `occurredAt`, `type`, `version` y `correlationId` en el sobre.
- **SHOULD** tener brokers locales equivalentes funcionales para desarrollo; qué NO se reproduce en local respecto a AWS (políticas IAM, cuotas, latencias reales de SQS/SNS/MSK) debe declararse en la matriz AWS-local. Preparado para AWS, no verificado en real.

## Por qué
La asincronía desacopla en tiempo y disponibilidad, pero traslada la complejidad a duplicados, desorden y observabilidad. Sin outbox, un fallo entre commit y publicación pierde eventos o publica fantasmas.

## Ejemplos
### Mal
```java
@Transactional
public void place(Order o) {
    repo.save(o);
    kafkaTemplate.send("orders", o);   // si la tx hace rollback, el evento ya salió
}
```
### Bien
```java
@Transactional
public void place(Order o) {
    repo.save(o);
    outbox.save(OutboxMessage.of("OrderPlaced", o.id(), json(new OrderPlaced(o.id(), o.total()))));
}

void onMessage(Envelope e) {
    if (processed.existsById(e.eventId())) return;   // idempotencia
    handler.handle(e);
    processed.save(new ProcessedMessage(e.eventId()));
}
```
Ambas escrituras del consumidor deben ir en la misma transacción.

## Checklist de revisión
- [ ] Eventos en pasado; comandos separados.
- [ ] Outbox en lugar de publicar dentro de la transacción.
- [ ] Consumidores idempotentes y DLQ con alerta.
- [ ] Contrato versionado y documentado.
- [ ] No se asume orden global.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `send(` dentro de método `@Transactional` | 1 | pendiente: `policies/semgrep/` |
| Revisión de contratos y consumidores | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `sagas-and-process-managers`, `cqrs`, `event-sourcing`, `consistency-and-cap-tradeoffs`.
- Fuentes: microservices.io, "Transactional outbox" (Richardson); Hohpe y Woolf, "Enterprise Integration Patterns"..
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
