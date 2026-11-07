---
name: sql-injection-prevention
description: Usar al escribir cualquier consulta SQL/JPQL/HQL, ordenaciones dinámicas o filtros que reciban entrada de usuario.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Prevención de inyección SQL

## Cuándo aplicar y cuándo no
- Aplica a JPQL, HQL, SQL nativo, `JdbcTemplate`, jOOQ plain SQL y cualquier SQL generado.
- No aplica a SQL estático de migraciones (revisado en `schema-migrations`).

## Reglas
- **MUST** pasar todo valor externo como parámetro enlazado (`:name`, `?`), nunca por concatenación ni `String.format`.
- **MUST NOT** construir identificadores (columna, tabla, `ORDER BY`) con entrada de usuario; mapearlos desde una lista blanca (`enum` o `Map`).
- **MUST** validar `Sort` de Spring Data contra propiedades permitidas antes de aplicarlo en consultas nativas o `@Query` con `#{#sort}`.
- **MUST** escapar los comodines de `LIKE` del usuario (`%`, `_`) cuando se busque literal.
- **SHOULD** usar `Specification`/Criteria o jOOQ con DSL tipado para filtros dinámicos.
- **MUST NOT** construir `IN (...)` concatenando; usar parámetro de colección.
- **MUST** conectar con un usuario de BD de mínimos privilegios (sin DDL en runtime).
- **MUST NOT** devolver mensajes de error SQL al cliente (ver `error-handling-problem-details`).

## Por qué
Una sola concatenación abre ejecución arbitraria de SQL con los privilegios de la aplicación. Los parámetros enlazados separan código de datos; la lista blanca cubre lo que no se puede parametrizar (identificadores).

## Ejemplos
### Mal
```java
String jpql = "select u from User u where u.name = '" + name + "' order by " + sortBy;
return em.createQuery(jpql, User.class).getResultList();
```
### Bien
```java
private static final Map<String, String> SORTABLE = Map.of("name", "u.name", "created", "u.createdAt");

public List<User> search(String name, String sortKey) {
    String column = SORTABLE.getOrDefault(sortKey, "u.name");   // lista blanca
    return em.createQuery(
            "select u from User u where u.name = :name order by " + column, User.class)
        .setParameter("name", name)
        .getResultList();
}
```
El único fragmento concatenado procede de constantes propias, nunca de la entrada.

## Checklist de revisión
- [ ] Cero concatenación de valores externos en consultas.
- [ ] Ordenación y columnas dinámicas desde lista blanca.
- [ ] `LIKE` con comodines escapados.
- [ ] Usuario de BD sin privilegios DDL.
- [ ] Errores SQL no expuestos al cliente.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: concatenación en `createQuery`/`createNativeQuery`/JDBC | 1 | `policies/semgrep/sql-string-concat.yaml` |
| Escáner SAST en CI | 2 | pendiente (pipeline del proyecto generado) |
| Revisión de seguridad | 3 | agente `security-reviewer` |

> Estado: la regla Semgrep no se ha ejecutado en real (TODO-VERIFY). Solo detecta concatenación directa en el argumento, no flujos indirectos.

## Relacionados, fuentes y mantenimiento
- Relacionados: `query-strategy`, `owasp-top10-and-api-top10`, `jdbc-and-jooq`, `secure-sdlc-nist-ssdf`.
- Fuentes: OWASP SQL Injection Prevention Cheat Sheet — TODO-VERIFY URL; no consultada en vivo el 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
