---
name: injection-families
description: Usar al construir consultas SQL/JPQL, NoSQL, LDAP, comandos de SO, plantillas o expresiones SpEL con datos externos, para prevenir inyección.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Familias de inyección

## Cuándo aplicar y cuándo no
- Aplica a cualquier código que combine datos no confiables (request, cabeceras, mensajes, ficheros, BD) con un intérprete: SQL/JPQL, MongoDB/DynamoDB, LDAP, shell, plantillas, SpEL, XPath.
- No aplica a validación de formato en general (ver `input-validation-output-encoding`) ni a XSS en el navegador (codificación de salida).

## Reglas
- **MUST** usar consultas parametrizadas (`PreparedStatement`, parámetros nombrados JPA, Spring Data derivadas) en todo acceso SQL.
- **MUST NOT** concatenar ni formatear (`+`, `String.format`, text blocks interpolados) datos externos dentro de SQL/JPQL/HQL.
- **MUST** validar con lista cerrada (allowlist) los identificadores dinámicos que no se pueden parametrizar (columna de `ORDER BY`, nombre de tabla).
- **MUST NOT** invocar `Runtime.exec`/`ProcessBuilder` con una cadena de shell; si es inevitable, pasar argumentos como lista, sin `sh -c`, con ejecutable fijo.
- **MUST NOT** evaluar entrada externa con `SpelExpressionParser`, motores de plantillas o `ScriptEngine`; usar `SimpleEvaluationContext` si hace falta SpEL.
- **MUST** construir filtros NoSQL con la API tipada del driver (`Filters.eq`), nunca parseando JSON del cliente como filtro.
- **MUST** escapar filtros y DN de LDAP con la API del framework (`LdapEncoder`/filtros de Spring LDAP) y no concatenarlos.
- **SHOULD** ejecutar la aplicación con un usuario de BD de mínimo privilegio, de modo que una inyección tenga radio de daño limitado.
- **SHOULD** devolver errores genéricos al cliente; el detalle SQL va al log.

## Por qué
La inyección ocurre cuando datos y código comparten canal. Parametrizar separa ambos de forma estructural; el escapado manual falla por contexto y por dialecto. Los identificadores no se pueden enlazar como parámetro, por eso requieren allowlist. Referencia general: OWASP Injection Prevention Cheat Sheet (consultada 2026-11-07; TODO-VERIFY URL vigente).

## Ejemplos
### Mal
```java
String sql = "SELECT * FROM users WHERE email = '" + email + "' ORDER BY " + sort;
return jdbc.query(sql, mapper);   // email = "x' OR '1'='1"
```
```java
new ProcessBuilder("sh", "-c", "convert " + fileName + " out.png").start();
```
### Bien
```java
private static final Set<String> SORTABLE = Set.of("created_at", "email");

String col = SORTABLE.contains(sort) ? sort : "created_at";
String sql = "SELECT id, email FROM users WHERE email = :email ORDER BY " + col;
return named.query(sql, Map.of("email", email), mapper);
```
```java
// JPA: parametro nombrado
em.createQuery("select u from User u where u.email = :email", User.class)
  .setParameter("email", email).getResultList();
// Proceso: ejecutable fijo, argumentos separados, nombre validado antes
new ProcessBuilder("/usr/bin/convert", safeFile.toString(), "out.png").start();
```

## Checklist de revisión
- [ ] Ningún SQL/JPQL se construye con `+` o `format` sobre datos externos.
- [ ] Los `ORDER BY`/nombres dinámicos pasan por allowlist.
- [ ] No hay `sh -c` ni `Runtime.exec(String)` con entrada externa.
- [ ] No se evalúa SpEL/plantillas con contexto completo sobre datos de usuario.
- [ ] Filtros NoSQL/LDAP usan API tipada.
- [ ] El usuario de BD de la app no es propietario del esquema.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: concatenación en SQL | 1 | `policies/semgrep/sql-string-concat.yaml` |
| Test de integración con payloads de inyección (`' OR '1'='1`) | 1 | tests del proyecto generado (pendiente de plantilla) |
| Revisión de seguridad de consultas dinámicas | 3 | agente `code-reviewer` |

> Regla Semgrep sin ejecutar aún en la fábrica (TODO-VERIFY).

## Relacionados, fuentes y mantenimiento
- Relacionados: `input-validation-output-encoding`, `owasp-top10-and-api-top10`, `deserialization-xxe-ssrf-traversal`, `n-plus-one`.
- Fuentes: OWASP Cheat Sheet Series (Injection Prevention, Query Parameterization, OS Command Injection) consultado 2026-11-07, TODO-VERIFY URL exacta.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
