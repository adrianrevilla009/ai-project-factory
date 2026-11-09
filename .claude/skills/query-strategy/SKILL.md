---
name: query-strategy
description: Usar al elegir cómo expresar una consulta (derived query, @Query, Criteria/Specification, SQL nativo, jOOQ).
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Estrategia de consultas

## Cuándo aplicar y cuándo no
- Aplica al añadir cualquier consulta nueva a un repositorio o DAO.
- No aplica a CRUD trivial (`findById`, `save`), que usa los métodos del repositorio.

## Reglas
- **MUST** elegir la herramienta más simple que cubra el caso: `findById`/derived query (1-2 criterios) → `@Query` JPQL (joins, proyecciones) → `Specification`/Criteria (filtros opcionales dinámicos) → SQL nativo o jOOQ (funciones del motor, CTE, ventanas, informes).
- **MUST NOT** usar derived queries con nombres de más de ~3 criterios (`findByStatusAndCustomerIdAndCreatedAtBetweenAndTotalGreaterThan...`): pasar a `@Query`.
- **MUST** parametrizar siempre (ver `sql-injection-prevention`).
- **SHOULD** centralizar filtros dinámicos en `Specification`s composables y testeadas, no en `if` que concatenan JPQL.
- **SHOULD** usar SQL nativo/jOOQ en informes complejos con DTO plano, aislado en un repositorio de lectura.
- **MUST** revisar el plan de ejecución de consultas nuevas sobre tablas grandes (ver `indexing-and-query-plans`).
- **MUST NOT** filtrar o ordenar en memoria (`stream().filter`) lo que la BD puede resolver.
- **MUST NOT** mezclar lecturas con 5+ joins en el repositorio del agregado; crear un repositorio de consulta.

## Por qué
Cada nivel de herramienta añade potencia y coste de mantenimiento. Derived queries largas son ilegibles; JPQL dinámico por concatenación es un vector de inyección; filtrar en memoria no escala.

## Ejemplos
### Mal
```java
List<Order> findByStatusAndCustomerIdAndCreatedAtBetweenAndTotalGreaterThanOrderByCreatedAtDesc(
    OrderStatus s, Long c, Instant from, Instant to, BigDecimal min);

var all = repo.findAll();
return all.stream().filter(o -> o.getTotal().compareTo(min) > 0).toList();
```
### Bien
```java
public final class OrderSpecs {
    private OrderSpecs() { }

    public static Specification<Order> hasStatus(OrderStatus s) {
        return (root, q, cb) -> s == null ? null : cb.equal(root.get("status"), s);
    }
    public static Specification<Order> totalAbove(BigDecimal min) {
        return (root, q, cb) -> min == null ? null : cb.greaterThan(root.get("total"), min);
    }
}

repo.findAll(Specification.where(hasStatus(status)).and(totalAbove(min)), pageable);
```
`Specification` requiere que el repositorio extienda `JpaSpecificationExecutor`.

## Checklist de revisión
- [ ] La herramienta elegida es la más simple posible.
- [ ] Sin filtrado en memoria.
- [ ] Filtros dinámicos mediante `Specification` o jOOQ, no concatenación.
- [ ] Plan de ejecución revisado en tablas grandes.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep contra concatenación en consultas | 1 | `policies/semgrep/sql-string-concat.yaml` |
| Revisión de consultas nuevas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `projections-and-dtos`, `sql-injection-prevention`, `jdbc-and-jooq`, `indexing-and-query-plans`, `spring-data-rules`.
- Fuentes: Spring Data JPA reference (query methods, Specifications).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
