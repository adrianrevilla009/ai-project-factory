---
name: event-sourcing
description: "Usar al evaluar o implementar event sourcing (estado como secuencia de eventos); por defecto se desaconseja salvo necesidad de auditoría o temporalidad."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# Event sourcing

## Cuándo aplicar y cuándo no
- Aplica si el negocio exige historial completo e inmutable, reconstrucción del estado en el tiempo o auditoría fuerte de cada cambio.
- No aplica por defecto ni solo "porque usamos eventos". Publicar eventos de integración (ver `event-driven`) no es event sourcing. No usar en CRUD, ni si el equipo no domina versionado de eventos.

## Reglas
- **MUST** documentar en un ADR por qué una tabla de auditoría o el historial CDC no basta.
- **MUST** tratar los eventos como inmutables y en pasado (`OrderPlaced`); la corrección se hace con un evento compensatorio, nunca editando.
- **MUST** versionar el esquema de eventos y escribir upcasters para eventos antiguos antes de cambiar su forma.
- **MUST** garantizar concurrencia optimista por stream (versión esperada al añadir eventos).
- **MUST** usar snapshots solo como optimización reconstruible, nunca como fuente de verdad.
- **MUST NOT** guardar el mismo estado además en una segunda tabla escrita por el comando (sin doble escritura); las vistas son proyecciones derivadas (ver `cqrs`).
- **MUST NOT** guardar datos personales directamente en eventos inmutables sin estrategia de borrado (cifrado por sujeto o referencias); consultar normativa vigente, borrador por confirmar con fuente oficial.
- **SHOULD** limitar los streams por aggregate (ver `ddd-tactical`).

## Por qué
Event sourcing da auditoría y viajes en el tiempo, a cambio de complejidad permanente: evolución de esquemas, reconstrucción, proyecciones eventuales y derecho de supresión. Es una decisión cara de revertir.

## Ejemplos
### Mal
```java
// "Event sourcing" que muta eventos y duplica estado
eventRepository.update(eventId, newPayload);
orderTable.update(orderId, status); // segunda fuente de verdad
```
### Bien
```java
public record OrderPlacedV2(String orderId, String customerId, long totalCents, String currency) {}

// Append con versión esperada (concurrencia optimista)
eventStore.append(streamId("order", orderId), expectedVersion, List.of(new OrderPlacedV2(...)));

// Upcaster V1 -> V2
OrderPlacedV2 upcast(OrderPlacedV1 old) {
    return new OrderPlacedV2(old.orderId(), old.customerId(), old.totalCents(), "EUR");
}
```
Esquema mínimo del almacén en Postgres:
```sql
create table event_store (
  stream_id text not null, version int not null, type text not null,
  payload jsonb not null, occurred_at timestamptz not null default now(),
  primary key (stream_id, version)
);
```

## Checklist de revisión
- [ ] ADR con alternativas descartadas (auditoría/CDC).
- [ ] Eventos inmutables, en pasado y versionados.
- [ ] Concurrencia optimista por stream.
- [ ] Proyecciones reconstruibles; sin segunda fuente de verdad.
- [ ] Estrategia para datos personales en eventos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del ADR en el gate de arquitectura | 4 | `gates/` |
| Revisión de código de eventos y upcasters | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cqrs`, `event-driven`, `ddd-tactical`, `consistency-and-cap-tradeoffs`.
- Fuentes: Fowler, "Event Sourcing" (martinfowler.com); Young, "Versioning in an Event Sourced System" (2017)..
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
