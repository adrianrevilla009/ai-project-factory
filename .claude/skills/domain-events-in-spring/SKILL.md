---
name: domain-events-in-spring
description: Usar al publicar o consumir eventos de dominio dentro de una aplicación Spring (ApplicationEventPublisher, Spring Modulith) y decidir qué sale a mensajería externa.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Eventos de dominio en Spring

## Cuándo aplicar y cuándo no
- Aplica a desacoplar módulos de un mismo proceso (p. ej. `orders` notifica a `billing`) y a preparar la publicación externa.
- No aplica a integración entre servicios (Kafka/SQS: bloque 06) ni a event sourcing (bloque 05).

## Reglas
- **MUST** nombrar eventos en pasado y como hechos de negocio (`OrderPlaced`), inmutables (`record`).
- **MUST** que el evento lleve identificadores y datos mínimos, no entidades JPA (evita `LazyInitializationException` y acoplamiento).
- **MUST** consumir con `@TransactionalEventListener(phase = AFTER_COMMIT)` cuando el efecto no deba ocurrir si la transacción hace rollback.
- **MUST** que los listeners con efectos externos sean idempotentes: pueden ejecutarse más de una vez.
- **SHOULD** usar `@ApplicationModuleListener` de Spring Modulith (asíncrono, transaccional propio) y su registro de publicación de eventos para no perder eventos tras un fallo.
- **MUST NOT** publicar a un broker desde el listener y escribir además en otra base de datos sin outbox (sin doble escritura; ver `outbox-and-cdc`).
- **MUST NOT** depender del orden entre listeners.
- **SHOULD** que el evento cruce el límite del módulo solo si está en su API pública (`project-layout`).

## Por qué
Los eventos en proceso reducen el acoplamiento entre módulos, pero comparten el hilo y la transacción por defecto: un listener lento o que falla puede romper al publicador. Separar fase y asincronía hace explícito qué garantías hay. Con Modulith, el registro de eventos da at-least-once dentro del proceso.

## Ejemplos
### Mal
```java
@Service
class OrderService {
    @Transactional
    void place(Order order) {
        repo.save(order);
        publisher.publishEvent(order);          // entidad JPA como evento
        kafkaTemplate.send("orders", order);    // envío antes del commit; sin outbox
    }
}
```
### Bien
```java
public record OrderPlaced(UUID orderId, UUID customerId, Instant occurredAt) {}

@Service
class OrderService {
    @Transactional
    void place(Order order) {
        repo.save(order);
        publisher.publishEvent(new OrderPlaced(order.getId(), order.getCustomerId(), Instant.now()));
    }
}

@Component
class BillingOnOrderPlaced {
    @ApplicationModuleListener
    void on(OrderPlaced event) {
        invoices.createFor(event.orderId());   // idempotente por orderId
    }
}
```

## Checklist de revisión
- [ ] Eventos son records inmutables con nombre en pasado.
- [ ] No viajan entidades JPA.
- [ ] Fase transaccional del listener elegida a propósito.
- [ ] Listeners idempotentes.
- [ ] Ningún envío a broker sin outbox.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: eventos no referencian tipos `@Entity` | 1 | `policies/archunit/` (pendiente) |
| Spring Modulith `ApplicationModules.verify()` en tests | 1 | tests del proyecto generado (pendiente) |
| Revisión humana/agente de listeners nuevos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `project-layout`, `event-driven`, `outbox-and-cdc`, `spring-data-rules`.
- Fuentes: Spring Framework (eventos de aplicación) y Spring Modulith reference.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
