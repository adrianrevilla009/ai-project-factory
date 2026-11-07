---
name: cqrs
description: "Usar al decidir si separar modelos de escritura y lectura (CQRS) y cómo mantener las proyecciones sin doble escritura."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# CQRS

## Cuándo aplicar y cuándo no
- Aplica cuando lectura y escritura tienen formas o cargas muy distintas (listados agregados, búsqueda, informes) o el modelo de dominio es rico.
- No aplica por defecto: un CRUD o un módulo con lecturas simples no necesita dos modelos. CQRS no implica event sourcing ni dos bases de datos.

## Reglas
- **MUST** separar comandos (cambian estado, no devuelven datos de negocio) de consultas (no cambian estado) a nivel de código: handlers distintos.
- **MUST** justificar en un ADR el paso a modelo de lectura separado (carga, forma, latencia); el nivel mínimo es misma BD con proyecciones/vistas.
- **MUST NOT** hacer doble escritura Postgres + NoSQL desde el comando (decisión 4.5); la proyección se alimenta desde eventos publicados con outbox o desde CDC.
- **MUST** tratar el modelo de lectura como derivado y reconstruible desde la fuente de verdad.
- **MUST** diseñar la UI y la API para consistencia eventual cuando la proyección sea asíncrona (mostrar estado pendiente, no asumir lectura inmediata).
- **SHOULD** empezar por el nivel 1 (mismo esquema, consultas con DTO/proyecciones) y subir solo con evidencia.
- **SHOULD** hacer proyecciones idempotentes (reaplicar un evento no cambia el resultado).
- **MUST NOT** devolver entidades JPA desde consultas; usar DTO de lectura.

## Por qué
Separar los modelos permite optimizar cada lado, pero introduce retraso, duplicación y operación extra. La mayoría de problemas de rendimiento de lectura se resuelven con proyecciones SQL antes de necesitar un segundo almacén.

## Ejemplos
### Mal
```java
@Transactional
public void placeOrder(PlaceOrder cmd) {
    orderRepository.save(order);          // Postgres
    orderSearchClient.index(order);       // NoSQL: doble escritura, puede divergir
}
```
### Bien
```java
// Comando: escribe el aggregate y el evento en la misma transacción (outbox)
@Transactional
public void handle(PlaceOrder cmd) {
    var order = Order.place(cmd.customerId(), cmd.lines());
    orders.save(order);
    outbox.append(new OrderPlaced(order.id(), order.total()));
}

// Consulta: DTO de lectura, sin tocar el aggregate
public interface OrderQueries {
    Page<OrderSummary> findSummaries(CustomerId customerId, Pageable page);
}

// Proyector idempotente (upsert por order_id)
@EventListener
void on(OrderPlaced e) { summaries.upsert(e.orderId(), e.total()); }
```

## Checklist de revisión
- [ ] Comandos y consultas en handlers separados.
- [ ] ADR que justifica cualquier modelo de lectura separado.
- [ ] Ninguna operación escribe en dos almacenes a la vez.
- [ ] Proyecciones idempotentes y reconstruibles.
- [ ] La API documenta consistencia eventual donde exista.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de ADR y de doble escritura | 3 | agente `code-reviewer` |
| Regla Semgrep contra doble escritura en un mismo método | 1 | pendiente: `policies/semgrep/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `event-driven`, `consistency-and-cap-tradeoffs`, `ddd-tactical`.
- Fuentes: Fowler, "CQRS" (martinfowler.com); Young, "CQRS Documents" (2010). TODO-VERIFY: URLs y fechas de consulta.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
