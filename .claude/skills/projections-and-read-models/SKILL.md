---
name: projections-and-read-models
description: "Usar al construir proyecciones o read models (Postgres, OpenSearch) a partir de eventos: idempotencia, orden, checkpoints y consistencia eventual; subskill de event-sourcing."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# Proyecciones y read models

## Cuándo aplicar y cuándo no
- Aplica a cualquier vista derivada de un event store (tabla Postgres, índice OpenSearch, caché Redis).
- No aplica a la lectura del propio agregado (se reconstruye de sus eventos). Subskill de `event-sourcing`; ver también `cqrs`.

## Reglas
- **MUST** tratar la proyección como derivada y descartable: se puede borrar y reconstruir desde los eventos (`rebuilds-and-replays`).
- **MUST NOT** escribir la proyección desde el comando, ni permitir que otro proceso la modifique; solo el consumidor de eventos escribe.
- **MUST** hacer el consumidor idempotente: guardar el `(streamId, version)` aplicado y descartar duplicados o eventos anteriores.
- **MUST** persistir el checkpoint (última posición) en la misma transacción que el cambio de la proyección cuando el destino es Postgres.
- **MUST** asumir entrega at-least-once y orden garantizado solo dentro de un stream; no depender del orden entre streams.
- **MUST** exponer en la API que la vista es eventualmente consistente (por ejemplo `lastAppliedVersion`) y no leer de ella para decidir un comando.
- **MUST NOT** guardar en la proyección datos que no deriven de eventos.
- **SHOULD** una proyección por necesidad de consulta; evitar la vista "universal".
- **SHOULD** monitorizar el retraso (lag) y alertar por encima de un umbral acordado.
- **MUST** aplicar las mismas reglas de supresión de datos personales a las proyecciones (`gdpr-and-immutable-events`).

## Por qué
Las proyecciones permiten leer rápido y de forma flexible, pero van por detrás de la escritura. Si los comandos las usan para decidir, o si se escriben a la vez que el store, se reintroduce la doble escritura. El checkpoint transaccional evita duplicados y huecos al reiniciar.

## Ejemplos
### Mal
```java
eventStore.append(stream, expected, events);
orderViewRepository.save(OrderView.from(events));   // el comando escribe la vista: doble escritura
```
### Bien
```java
@Transactional
public void on(StoredEvent e) {
    if (e.version() <= checkpoints.lastVersion(e.streamId())) return;     // idempotente
    switch (e.payload()) {
        case OrderPlacedV2 p -> orderViews.upsert(p.orderId(), p.customerId(), p.totalCents(), e.version());
        case OrderShipped s -> orderViews.markShipped(s.orderId(), e.version());
        default -> { }
    }
    checkpoints.advance(e.streamId(), e.version());                         // misma transacción
}
```
```sql
create table order_view (
  order_id text primary key, customer_id text not null, total_cents bigint not null,
  status text not null, last_version bigint not null
);
create table projection_checkpoint (stream_id text primary key, last_version bigint not null);
```

## Criterios de decisión y trampas
### Cómo decidir
- Proyecciones para necesidades de lectura concretas, idempotentes y reconstruibles desde los eventos; mide su retraso.
- Una proyección por caso de uso, no una gigante.
### Trampas frecuentes
- Proyecciones que no toleran el reprocesado de eventos.
- Lecturas que exigen datos recién escritos sin diseñar el retraso.
- Lógica de negocio en la proyección.
- Sin forma de reconstruir.
- Esquema de proyección sin versionar.
### Evidencia
- Una reconstrucción completa de la proyección produce el mismo resultado y su retraso se monitoriza.

## Checklist de revisión
- [ ] Solo el consumidor escribe la proyección.
- [ ] Idempotencia y checkpoint transaccional.
- [ ] Proyección reconstruible; hay procedimiento y tiempo estimado.
- [ ] La API indica consistencia eventual; los comandos no leen de la vista.
- [ ] Lag monitorizado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: el paquete de comandos no depende de repositorios de proyecciones | 1 | pendiente en `policies/archunit/` |
| Test de reproducción: duplicar eventos no cambia la vista | 1 | tests del proyecto generado |
| Revisión de consumidores y checkpoints | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `cqrs`, `cqrs-read-models-and-search`, `rebuilds-and-replays`, `idempotency-and-deduplication`, `delivery-semantics`.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
