---
name: datastore-selection-guide
description: "Usar al elegir el almacén de datos de un agregado o caso de uso (Postgres, DynamoDB, OpenSearch, Redis) y al decidir si hace falta persistencia políglota."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "review"
---

# Guía de selección de almacén de datos

## Cuándo aplicar y cuándo no
- Aplica al diseñar un agregado, un read model o una caché nuevos, o al proponer un segundo almacén en un proyecto.
- No aplica a elegir tablas o índices dentro de un almacén ya decidido (ver `db-design-conventions`, `dynamodb-data-modeling`).

## Reglas
- **MUST** partir de PostgreSQL (Aurora PostgreSQL en AWS) como almacén por defecto del estado (ADR-0013).
- **MUST** asignar a cada agregado UNA única fuente de verdad y anotarla en el ADR o en el mapa de datos del proyecto.
- **MUST** justificar por escrito cada almacén adicional: patrón de acceso que Postgres no cubre, volumen o latencia medidos o estimados, y coste operativo asumido (`polyglot-operations-cost`).
- **MUST NOT** escribir el mismo agregado a la vez en Postgres y en un almacén NoSQL desde el comando (doble escritura: no es atómica). Los otros almacenes son proyecciones derivadas de eventos u outbox.
- **SHOULD** usar DynamoDB solo para: event store, claves-valor con acceso conocido por clave, o volúmenes con picos que exigen escalado sin gestión.
- **SHOULD** usar OpenSearch solo como read model de búsqueda/texto y Redis solo como caché o estructura efímera: ninguno es fuente de verdad.
- **MUST NOT** introducir un almacén "por moda" o por currículum del equipo.

## Por qué
Cada almacén añade backups, migraciones, monitorización, seguridad, formación y modos de fallo propios. La persistencia políglota se paga siempre; el beneficio debe ser medible. Postgres cubre relacional, JSONB, búsqueda básica (`tsvector`) y colas ligeras, y suele bastar.

## Ejemplos
### Mal
```java
@Transactional
public void placeOrder(Order o) {
    orderRepository.save(o);            // Postgres
    dynamoTable.putItem(toItem(o));     // DynamoDB: segunda "verdad", si falla uno divergen
}
```
### Bien
```java
@Transactional
public void placeOrder(Order o) {
    orderRepository.save(o);                                   // única fuente de verdad
    outboxRepository.save(OutboxEvent.of("OrderPlaced", o.id(), payload(o))); // misma transacción
}
// Un consumidor del evento mantiene el read model en OpenSearch (proyección derivada).
```
Árbol de decisión resumido:
```text
¿Relacional/transaccional con joins?            -> PostgreSQL
¿Los eventos SON el negocio (historia, saldos)? -> event store en DynamoDB (dynamodb-event-store)
¿Acceso solo por clave, picos impredecibles?    -> DynamoDB
¿Búsqueda de texto/facetas sobre datos ajenos?  -> proyección en OpenSearch
¿Lectura repetida cara, dato reconstruible?     -> caché Redis (cache-strategies)
```

## Checklist de revisión
- [ ] Cada agregado tiene una sola fuente de verdad documentada.
- [ ] Cada almacén extra tiene justificación y coste operativo anotados.
- [ ] No hay escritura simultánea en dos almacenes desde el mismo comando.
- [ ] Redis y OpenSearch figuran como derivados, no como origen.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión del mapa de datos/ADR en el gate de arquitectura | 4 | `gates/` (revisión humana) |
| Revisión de código: dos escrituras a almacenes distintos en un mismo método | 3 | agente `code-reviewer` |
| Regla Semgrep contra doble escritura | 1 | pendiente (no existe todavía) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `polyglot-operations-cost`, `outbox-and-cdc`, `cqrs`, `event-sourcing`, `consistency-and-cap-tradeoffs`, `data-sync-pitfalls`.
- Decisiones: ADR-0013, ADR-0014; brief 4.5.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
