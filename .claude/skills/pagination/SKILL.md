---
name: pagination
description: Usar al paginar consultas en base de datos (offset vs keyset, Page vs Slice, orden estable, conteos costosos).
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Paginación en base de datos

## Cuándo aplicar y cuándo no
- Aplica a cualquier consulta que devuelva un conjunto potencialmente grande.
- No aplica al contrato HTTP de paginación (parámetros, enlaces): ver `pagination-filter-sort` (bloque API).

## Reglas
- **MUST** limitar toda consulta de listado; ningún endpoint devuelve "todo" sin tope máximo de tamaño de página.
- **MUST** definir un orden total y determinista (`ORDER BY created_at, id`): sin desempate, las páginas duplican u omiten filas.
- **SHOULD** usar paginación por keyset (`where (created_at, id) > (:ts, :id)`) en tablas grandes o scroll infinito; `OFFSET` degrada linealmente con la profundidad.
- **SHOULD** devolver `Slice` (sin `count(*)`) cuando la UI no necesita el total.
- **MUST** dar a `Page` un `countQuery` propio si la consulta tiene joins o fetch (ver `joins-and-fetch-joins`).
- **MUST NOT** combinar `JOIN FETCH` de colección con paginación (se pagina en memoria).
- **MUST** respaldar el orden de paginación con un índice (ver `indexing-and-query-plans`).
- **MUST NOT** aceptar `size` sin validar (`@Max`) ni `sort` sin lista blanca.

## Por qué
`OFFSET 1000000` obliga al motor a leer y descartar un millón de filas. Un orden no determinista rompe la consistencia entre páginas. El `count(*)` puede costar más que la propia página.

## Ejemplos
### Mal
```java
@Query("select o from Order o order by o.createdAt")   // empates sin desempate
Page<Order> findAllOrdered(Pageable pageable);          // size sin tope, count con el join
```
### Bien
```java
public record OrderCursor(Instant createdAt, Long id) { }

@Query("""
    select new com.acme.orders.OrderSummary(o.id, o.createdAt, o.total)
    from Order o
    where (o.createdAt > :ts or (o.createdAt = :ts and o.id > :id))
    order by o.createdAt, o.id
    """)
List<OrderSummary> nextPage(Instant ts, Long id, Pageable limit); // PageRequest.of(0, 50)
```
```sql
CREATE INDEX idx_orders_created_id ON orders (created_at, id);
```

## Checklist de revisión
- [ ] Tamaño máximo de página validado.
- [ ] Orden total con desempate por id.
- [ ] Keyset en tablas grandes; `Slice` si no hace falta total.
- [ ] `countQuery` explícita si hay joins.
- [ ] Índice que cubre el orden.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validación `@Max` del tamaño en controladores | 1 | pendiente (regla ArchUnit/Semgrep) |
| Test de consultas con volumen y plan | 2 | pendiente (`db-testing`) |
| Revisión de consultas de listado | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `pagination-filter-sort`, `joins-and-fetch-joins`, `indexing-and-query-plans`, `projections-and-dtos`.
- Fuentes: Spring Data commons reference (paging, `Slice`, scrolling).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
