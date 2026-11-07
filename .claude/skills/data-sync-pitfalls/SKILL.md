---
name: data-sync-pitfalls
description: "Usar al sincronizar datos entre datastores (SQL, DynamoDB, OpenSearch, Redis) por eventos, CDC o jobs, para evitar divergencias, pérdidas, duplicados y desorden."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Trampas de la sincronización de datos

## Cuándo aplicar y cuándo no
- Aplica a cualquier réplica derivada: índices, vistas, cachés, copias analíticas, tablas de otro servicio.
- No aplica a réplicas físicas del mismo motor (ver `read-replicas-and-routing`).

## Reglas
- **MUST** declarar un único dueño (fuente de verdad) por dato; el resto son derivados reconstruibles. Sin doble escritura Postgres+NoSQL (4.5).
- **MUST** asumir entrega al-menos-una-vez y fuera de orden entre claves: handlers idempotentes y con versión/secuencia (descartar si `incoming.version <= stored.version`).
- **MUST** tratar el borrado explícitamente: propagar tombstones/eventos de borrado; un `upsert` ciego deja "zombis".
- **MUST** tener un job de reconciliación periódico (conteos, checksums por rango) y un procedimiento de resincronización completa.
- **MUST** monitorizar lag y antigüedad del evento más viejo sin procesar, con alerta.
- **MUST** dimensionar el relay para su ventana de retención: DynamoDB Streams guarda 24 h; si el consumidor está caído más tiempo hay pérdida y se requiere resincronización completa desde la tabla. Kinesis Data Streams for DynamoDB admite retención de hasta 1 año.
- **MUST NOT** asumir atomicidad ni orden entre ítems en Streams: los registros de una misma transacción pueden llegar en momentos distintos e intercalados.
- **MUST NOT** sincronizar con "dual write + reintento" ni con triggers que llaman a sistemas externos dentro de la transacción.
- **SHOULD** versionar el esquema del evento de sincronización (ver `schema-registry-and-evolution`).
- **SHOULD** usar zona horaria UTC y `Instant` para marcas de tiempo; no resolver conflictos con relojes de pared salvo documentarlo.

## Por qué
Casi todos los incidentes de sincronización vienen de cuatro causas: duplicados, desorden, borrados perdidos y lag no observado. Las defensas (idempotencia, versiones, tombstones, reconciliación) son baratas de diseñar al inicio y muy caras de añadir tras la primera divergencia.

## Ejemplos
### Mal
```java
public void onChange(ProductChanged e) {
    index.save(toDoc(e));            // upsert ciego: reorden pisa dato nuevo con antiguo
}                                    // y no existe camino para ProductDeleted
```
### Bien
```java
public void onChange(ProductEvent e) {
    if (e instanceof ProductDeleted d) { index.delete(d.productId(), d.version()); return; }
    var c = (ProductChanged) e;
    index.indexIfNewer(c.productId(), c.version(), toDoc(c));   // version externa
}
// Job nocturno: compara count y hash por rango de ids entre fuente e indice; reindexa discrepancias.
```

## Checklist de revisión
- [ ] Dueño único del dato identificado.
- [ ] Handlers idempotentes con versión; borrados propagados.
- [ ] Lag monitorizado con alerta; retención del relay > peor caída tolerada.
- [ ] Reconciliación periódica y resincronización completa documentadas.
- [ ] Sin escrituras duales.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de consumidores de sincronización | 3 | agente `code-reviewer` |
| Regla Semgrep para consumidores sin comparación de versión | pendiente | `policies/semgrep/` (no existe aún) |
| Alerta de lag y edad del outbox | 4 | revisión humana en el diseño de observabilidad del proyecto generado |

## Relacionados, fuentes y mantenimiento
- Relacionados: `outbox-and-cdc`, `cqrs-read-models-and-search`, `cache-strategies`, `idempotency-and-deduplication`, `consistency-and-sagas`.
- Fuentes (verificadas 2026-11-07): https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/streamsmain.html · https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
