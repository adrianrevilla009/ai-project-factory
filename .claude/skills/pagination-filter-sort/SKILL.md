---
name: pagination-filter-sort
description: "Usar al exponer colecciones en una API: paginación (offset o cursor), filtros y ordenación con límites seguros."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Paginación, filtrado y ordenación

## Cuándo aplicar y cuándo no
- Aplica a todo endpoint que devuelva una colección potencialmente no acotada.
- No aplica a recursos con cardinalidad fija y pequeña (p. ej. lista de países), que pueden documentarse como no paginados.

## Reglas
- **MUST** paginar toda colección; **MUST NOT** devolver listas sin límite.
- **MUST** imponer `size` máximo en servidor (p. ej. 100) y un valor por defecto; rechazar o recortar valores superiores de forma documentada.
- **MUST** usar paginación por cursor (keyset) para datos grandes o que cambian; offset solo para listados pequeños y estables.
- **MUST** hacer la ordenación determinista: añadir un desempate único (`id`) al `ORDER BY`.
- **MUST** validar con lista blanca los campos de `sort` y `filter`; **MUST NOT** concatenarlos en SQL/JPQL.
- **MUST** devolver metadatos: `items`, `nextCursor` (o `page`/`totalElements` si offset) y no exponer cursores interpretables (opacos, firmados o base64 de contenido no sensible).
- **SHOULD** evitar `count(*)` total en tablas grandes; ofrecer `hasMore`.
- **SHOULD** usar sintaxis uniforme: `?size=50&cursor=...&sort=createdAt:desc&status=PAID`.

## Por qué
Offset profundo es O(n) en la base de datos y devuelve duplicados o huecos si hay inserciones. Keyset mantiene coste constante. La lista blanca evita inyección y ordenaciones sobre columnas sin índice.

## Ejemplos
### Mal
```java
@GetMapping("/orders")
List<Order> list(@RequestParam String sort) {
    return em.createQuery("select o from Order o order by " + sort).getResultList();
}
```
### Bien
```java
@GetMapping("/orders")
OrderPage list(@RequestParam(defaultValue = "50") @Max(100) int size,
               @RequestParam(required = false) String cursor) {
    var after = Cursor.decode(cursor);               // (createdAt, id) opaco
    List<OrderSummary> rows = repo.findPage(after.createdAt(), after.id(), PageRequest.ofSize(size + 1));
    boolean more = rows.size() > size;
    return new OrderPage(rows.stream().limit(size).toList(),
                         more ? Cursor.encode(rows.get(size - 1)) : null);
}
// JPQL: where (o.createdAt, o.id) < (:ts, :id) order by o.createdAt desc, o.id desc
```
Comprobar que el motor/Hibernate soporta la comparación de tuplas; si no, expandirla (TODO-VERIFY).

## Checklist de revisión
- [ ] Toda colección paginada con `size` máximo.
- [ ] Orden con desempate único e índice que lo soporte.
- [ ] `sort`/`filter` contra lista blanca.
- [ ] Cursor opaco; sin `count(*)` caro por defecto.
- [ ] Parámetros y respuesta descritos en OpenAPI.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep: concatenación en `createQuery` | 1 | pendiente: `policies/semgrep/` (relacionado con `injection-families`) |
| Revisión de endpoints de listado | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rest-design-guidelines`, `openapi-contract-first`, `n-plus-one`, `rate-limiting-quotas`.
- Fuentes: documentación de Spring Data (`Window`/`ScrollPosition` para keyset) — TODO-VERIFY disponibilidad por versión.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
