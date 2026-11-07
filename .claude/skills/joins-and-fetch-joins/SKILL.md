---
name: joins-and-fetch-joins
description: Usar al escribir JPQL/Criteria con joins, JOIN FETCH, EntityGraph o al ver MultipleBagFetchException y paginación en memoria.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Joins y fetch joins

## Cuándo aplicar y cuándo no
- Aplica a consultas JPQL, HQL, Criteria y `@EntityGraph` que combinan entidades.
- No aplica a SQL nativo con DTO plano (ver `jdbc-and-jooq`).

## Reglas
- **MUST** distinguir `JOIN` (filtra/une, no inicializa) de `JOIN FETCH` (inicializa la asociación en la entidad).
- **MUST NOT** hacer `JOIN FETCH` de más de una colección (`List`) en la misma consulta: producto cartesiano y `MultipleBagFetchException`. Cargar la segunda con otra consulta o `@BatchSize`.
- **MUST NOT** combinar `JOIN FETCH` de colección con `Pageable`/`setMaxResults`: Hibernate pagina en memoria (aviso `HHH000104`). Paginar ids primero y luego cargar con fetch.
- **MUST** usar `DISTINCT` (o `Set`) solo cuando el fetch de colección duplica la raíz; comprobar si la versión de Hibernate ya deduplica (TODO-VERIFY).
- **SHOULD** usar `LEFT JOIN FETCH` si la asociación puede faltar; `JOIN FETCH` interno descarta filas sin relación.
- **SHOULD** preferir `@EntityGraph` en repositorios Spring Data para casos simples y `JOIN FETCH` explícito para los complejos.
- **MUST NOT** filtrar sobre un alias de `JOIN FETCH` de colección: la colección cargada queda incompleta.

## Por qué
Los fetch joins son la herramienta correcta contra N+1, pero mal usados causan resultados duplicados, explosión de filas o paginación en memoria que satura el heap con tablas grandes.

## Ejemplos
### Mal
```java
@Query("select o from Order o join fetch o.lines join fetch o.payments")
Page<Order> findAllWithAll(Pageable pageable); // dos bags + paginación en memoria
```
### Bien
```java
@Query("select o.id from Order o where o.status = :status")
Page<Long> findIdsByStatus(OrderStatus status, Pageable pageable);

@Query("select distinct o from Order o left join fetch o.lines where o.id in :ids")
List<Order> findWithLinesByIdIn(Collection<Long> ids);

// segunda colección en una consulta aparte (misma sesión, la entidad ya está gestionada)
@Query("select distinct o from Order o left join fetch o.payments where o.id in :ids")
List<Order> findWithPaymentsByIdIn(Collection<Long> ids);
```

## Checklist de revisión
- [ ] Como máximo una colección por fetch join.
- [ ] Ningún `JOIN FETCH` de colección con paginación.
- [ ] `LEFT JOIN FETCH` cuando la relación es opcional.
- [ ] Sin filtros sobre el alias de la colección cargada.
- [ ] Test de conteo de sentencias en consultas críticas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `join fetch` junto a `Pageable` | 1 | pendiente (`policies/semgrep/`) |
| Log/aviso `HHH000104` tratado como fallo en tests | 2 | pendiente (configuración de tests del proyecto generado) |
| Revisión de consultas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `n-plus-one`, `lazy-vs-eager`, `pagination`, `projections-and-dtos`.
- Fuentes: guía de usuario de Hibernate ORM (HQL, fetching) — TODO-VERIFY versión, URL y comportamiento de `DISTINCT`.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
