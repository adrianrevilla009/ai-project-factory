---
name: jdbc-and-jooq
description: Usar al elegir entre JPA, JdbcTemplate/JdbcClient y jOOQ, o al escribir consultas SQL explícitas, informes y lecturas complejas.
metadata:
  block: "03-persistence-sql"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# JDBC y jOOQ

## Cuándo aplicar y cuándo no
- Aplica a lecturas complejas (informes, agregaciones, joins múltiples), operaciones masivas y rutas críticas de rendimiento donde JPA estorba.
- No aplica al CRUD de agregados normal, donde JPA/Spring Data basta (ver `query-strategy`, `spring-data-rules`).

## Reglas
- **MUST** parametrizar siempre: `?`/parámetros nombrados o los bind values de jOOQ; nunca concatenar entrada en el SQL (ver `sql-injection-prevention`).
- **MUST** documentar la elección en `query-strategy`: JPA para escritura de agregados, SQL explícito para lecturas complejas (CQS pragmático).
- **MUST** mantener una sola vía de escritura por agregado; no mezclar JPA y SQL directo sobre la misma tabla dentro de una transacción sin hacer `flush()` antes y `clear()` después.
- **MUST** que JDBC/jOOQ usen el mismo `DataSource` y transacción de Spring (`DataSourceTransactionManager`/`JpaTransactionManager` con el mismo `DataSource`) para participar de `@Transactional`.
- **MUST NOT** devolver `ResultSet` ni tipos de jOOQ (`Record`) fuera de la capa de persistencia; mapear a DTOs/records.
- **SHOULD** preferir `JdbcClient`/`NamedParameterJdbcTemplate` sobre `JdbcTemplate` con `Object[]` posicional (comprobar disponibilidad de `JdbcClient` según versión de Spring).
- **SHOULD** con jOOQ, generar el código desde el esquema real de las migraciones (en build) para que el compilador detecte cambios de esquema. Usar la edición OSS (D16): confirmar que el dialecto necesario está en la edición Open Source (comprobar licencia).
- **SHOULD** usar `batchUpdate` para escrituras masivas (ver `batching-and-bulk-ops`).

## Por qué
JPA es excelente para agregados y mediocre para informes; forzarlo produce consultas JPQL ilegibles o N+1. SQL explícito da control del plan y de las proyecciones, pero pierde seguridad de tipos y portabilidad salvo que se use jOOQ. Dos vías sobre la misma tabla causan lecturas obsoletas del contexto de persistencia.

## Ejemplos
### Mal
```java
String sql = "select id, name from customer where name like '%" + term + "%'";
return jdbc.query(sql, (rs, i) -> new CustomerRow(rs.getLong(1), rs.getString(2)));
```
### Bien
```java
public List<CustomerRow> search(String term) {
    return jdbcClient.sql("""
            select id, name from customer
            where name ilike :pattern
            order by name limit 50
            """)
        .param("pattern", "%" + escapeLike(term) + "%")
        .query((rs, i) -> new CustomerRow(rs.getLong("id"), rs.getString("name")))
        .list();
}
```
```java
// jOOQ: tipado y con bind values
return dsl.select(CUSTOMER.ID, CUSTOMER.NAME)
          .from(CUSTOMER)
          .where(CUSTOMER.NAME.containsIgnoreCase(term))
          .fetch(r -> new CustomerRow(r.get(CUSTOMER.ID), r.get(CUSTOMER.NAME)));
```

## Checklist de revisión
- [ ] Ninguna concatenación de entrada en SQL.
- [ ] La consulta está en una clase de persistencia y devuelve DTOs.
- [ ] Comparte `DataSource` y transacción con el resto.
- [ ] No hay doble escritura JPA+SQL sobre la misma tabla sin `flush`/`clear`.
- [ ] Si se usa jOOQ, el código se genera del esquema migrado y la licencia es OSS.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: concatenación en `jdbcTemplate.query/update` | 1 | pendiente (`policies/semgrep/`, ver `sql-injection-prevention`) |
| Revisión de la elección JPA vs. SQL | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `query-strategy`, `sql-injection-prevention`, `projections-and-dtos`, `batching-and-bulk-ops`.
- Fuentes: Spring Framework Reference (Data Access, JDBC) y manual de jOOQ (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
