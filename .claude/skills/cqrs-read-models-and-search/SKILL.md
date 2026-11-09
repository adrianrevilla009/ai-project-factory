---
name: cqrs-read-models-and-search
description: "Usar al construir un read model o índice de búsqueda (OpenSearch) derivado de la base de datos de escritura, con consistencia eventual y sin doble escritura."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Read models CQRS y búsqueda (OpenSearch)

## Cuándo aplicar y cuándo no
- Aplica cuando las consultas (full-text, facetas, filtros combinados, agregaciones) no encajan en el modelo transaccional y se necesita un índice o vista separada.
- No aplica si un índice SQL o un `LIKE`/`tsvector` de Postgres resuelve la consulta (ver `indexing-and-query-plans`, `query-strategy`). Para el patrón en sí ver `cqrs`.

## Reglas
- **MUST** que la fuente de verdad sea una sola (Postgres o DynamoDB); OpenSearch es una proyección derivada y reconstruible. Sin doble escritura Postgres+NoSQL desde el comando (4.5).
- **MUST** alimentar el índice desde `outbox-and-cdc` (eventos o CDC) con un indexador idempotente: documento con `_id` = id de negocio y versión externa para descartar eventos antiguos.
- **MUST** poder reindexar todo desde la fuente (alias + índice versionado `products_v2`, conmutar el alias al terminar; ver `rebuilds-and-replays`).
- **MUST** que la UI/API acepte consistencia eventual: tras escribir, la búsqueda puede tardar en reflejar; leer-tu-escritura se resuelve consultando la fuente por id.
- **MUST NOT** usar el índice de búsqueda como fuente de verdad ni para validaciones de negocio (unicidad, saldos).
- **MUST NOT** guardar datos que el usuario no debería ver: aplicar el filtrado de autorización/tenant también en la consulta de búsqueda (ver `multi-tenancy`).
- **SHOULD** definir mappings explícitos (no dynamic mapping abierto) y versionarlos en el repo.
- **SHOULD** vigilar el lag de indexación y exponerlo como métrica.

## Por qué
La búsqueda y los listados complejos escalan y se modelan distinto que las escrituras. Separar permite optimizar cada lado, a costa de consistencia eventual y de operar otro sistema (ver `polyglot-operations-cost`). Si el índice se puede reconstruir, un fallo es una incomodidad, no una pérdida. Parámetros del motor (p. ej. intervalo de refresh del índice) comprobar contra documentación vigente de OpenSearch.

## Ejemplos
### Mal
```java
@Transactional
public void rename(UUID id, String name) {
    productRepo.save(product.rename(name));
    searchClient.index(toDoc(product)); // doble escritura: si falla uno, divergen
}
```
### Bien
```java
// Consumidor de eventos del outbox (idempotente, version externa)
public void on(ProductRenamed e) {
    client.index(i -> i.index("products_write").id(e.productId())
        .versionType(VersionType.External).version(e.version())
        .document(new ProductDoc(e.productId(), e.name())));
}
```
Los métodos exactos del cliente Java de OpenSearch se comprueban contra la versión usada.

## Checklist de revisión
- [ ] Una sola fuente de verdad; el índice se alimenta de eventos/CDC.
- [ ] Indexador idempotente y con versión.
- [ ] Alias + reindexado completo documentado.
- [ ] La UI tolera consistencia eventual.
- [ ] Autorización/tenant aplicados en la consulta.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión: ningún cliente de búsqueda invocado desde servicios transaccionales de escritura | 3 | agente `code-reviewer` |
| Regla ArchUnit: dominio/aplicación no dependen del cliente OpenSearch | pendiente | `policies/archunit/` (ver `HexagonalArchitectureRules.java` como base) |

OpenSearch gestionado en AWS: preparado para AWS, no verificado en real. En local se usa OpenSearch OSS en contenedor; no se reproducen dimensionado, alta disponibilidad ni control de acceso a nivel de dominio de AWS.

## Relacionados, fuentes y mantenimiento
- Relacionados: `cqrs`, `outbox-and-cdc`, `projections-and-read-models`, `search-and-discovery`, `data-sync-pitfalls`.
- Fuentes: documentación de OpenSearch.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
