---
name: search-and-discovery
description: "Usar al añadir búsqueda de texto, filtros/facetas o autocompletado: PostgreSQL FTS vs OpenSearch, indexación derivada y consistencia."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Búsqueda y descubrimiento

## Cuándo aplicar y cuándo no
- Aplica a búsqueda textual, facetas, ranking, autocompletado y búsqueda sobre varios agregados.
- No aplica a filtros por clave simple ya cubiertos por índices SQL ni a analítica pesada (otro bloque).

## Reglas
- **MUST** empezar por PostgreSQL (índices, `tsvector`/GIN, `pg_trgm`) si el volumen y los requisitos lo permiten; justificar en ADR el paso a un motor de búsqueda dedicado.
- **MUST** tratar el índice de búsqueda como **vista derivada y reconstruible**: la fuente de verdad es la BD transaccional. Sin doble escritura síncrona Postgres+índice (4.5); alimentar vía outbox/CDC (`outbox-and-cdc`).
- **MUST** poder reindexar completo sin downtime (alias + índice versionado).
- **MUST** aplicar autorización/tenant como filtro obligatorio en cada consulta al índice.
- **MUST** paginar con límite máximo; `search_after`/keyset en vez de offset profundo.
- **MUST NOT** exponer el motor de búsqueda directamente al navegador.
- **MUST NOT** indexar campos sensibles que no se vayan a buscar.
- **SHOULD** preferir OpenSearch (código abierto, Apache 2.0 según su repositorio: licencia TODO-VERIFY) sobre soluciones con licencia restrictiva (D16). Preparado para AWS (Amazon OpenSearch Service), no verificado en real; local con contenedor OpenSearch, sin reproducir dimensionado, multi-AZ ni cifrado del servicio gestionado.

## Por qué
Un índice como fuente de verdad pierde datos al reconstruirse; una doble escritura diverge ante fallos parciales. Sin filtro de tenant obligatorio, la búsqueda filtra datos entre clientes.

## Ejemplos
### Mal
```java
orderRepository.save(order);
searchClient.index(order); // doble escritura: si falla, divergen
```
### Bien
```sql
-- Postgres FTS suficiente para empezar
ALTER TABLE product ADD COLUMN search tsvector
  GENERATED ALWAYS AS (to_tsvector('spanish', name || ' ' || coalesce(description, ''))) STORED;
CREATE INDEX product_search_idx ON product USING GIN (search);
```
```java
// Filtro de tenant siempre inyectado
var query = bool().filter(term("tenantId", ctx.tenantId())).must(match("name", text)).build();
```

## Checklist de revisión
- [ ] Justificado el motor dedicado frente a Postgres.
- [ ] Índice alimentado por outbox/CDC; reindexado documentado.
- [ ] Filtro de tenant/autorización en toda consulta.
- [ ] Paginación acotada; motor no expuesto al cliente.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `searchClient.index` junto a `repository.save` en el mismo método | 1 | pendiente |
| Test de aislamiento de tenant en búsqueda | 1 | tests del proyecto generado |
| ADR de elección de motor | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `outbox-and-cdc`, `multi-tenancy`, `pii-and-data-classification`.
- Fuentes: PostgreSQL docs (Full Text Search): TODO-VERIFY URL. OpenSearch docs (https://docs.opensearch.org/docs/latest/, 2026-11-07; no confirma licencia en la página).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
