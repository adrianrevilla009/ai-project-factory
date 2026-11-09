---
name: connection-pooling
description: Usar al configurar o diagnosticar el pool de conexiones (HikariCP) o al dimensionar conexiones a PostgreSQL por instancia y servicio.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Pool de conexiones (HikariCP)

## Cuándo aplicar y cuándo no
- Aplica a `spring.datasource.hikari.*`, agotamiento de conexiones, timeouts de obtención y dimensionado frente a `max_connections` de PostgreSQL.
- No aplica a pools HTTP (ver `http-clients-and-timeouts`) ni a bases NoSQL con su propio cliente.

## Reglas
- **MUST** usar HikariCP (defecto de Spring Boot) con `maximum-pool-size` explícito; no heredar el defecto sin pensarlo.
- **MUST** dimensionar pequeño: el total de conexiones es `instancias x maximum-pool-size` y debe caber en `max_connections` de la BD con margen para mantenimiento y otros servicios.
- **MUST** fijar `connection-timeout` (fallar rápido, no esperar el defecto) y `max-lifetime` menor que cualquier timeout de red/proxy/BD intermedio.
- **MUST NOT** mantener una conexión mientras se hace I/O lento externo (HTTP, colas) dentro de una transacción (ver `transactions`).
- **MUST NOT** subir el pool como respuesta a "pool agotado" sin buscar antes transacciones largas o fugas.
- **SHOULD** activar `leak-detection-threshold` en entornos no productivos para detectar fugas.
- **SHOULD** exponer métricas del pool (`hikaricp.connections.*` vía Micrometer) y alertar sobre `pending` > 0 sostenido.
- **SHOULD** considerar un pooler externo (PgBouncer) cuando haya muchas instancias; revisar compatibilidad con prepared statements y modo de transacción.
- **SHOULD** usar pools separados para cargas distintas (online vs. batch) para que una no deje sin conexiones a la otra.

## Por qué
Un pool grande no da más rendimiento: la BD tiene un número limitado de núcleos y discos, y más conexiones activas solo aumentan la contención. Un pool pequeño con transacciones cortas rinde más. Cuando un servicio escala horizontalmente, el pool multiplicado puede agotar la BD completa. Los valores concretos dependen de la carga: medir.

## Ejemplos
### Mal
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 200      # x 10 instancias = 2000 conexiones
```
### Bien
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10
      minimum-idle: 10
      connection-timeout: 2000     # ms
      max-lifetime: 1500000        # ms, menor que el timeout del proxy/BD
      leak-detection-threshold: 20000   # solo en dev/test
```
Cálculo documentado en el servicio: 6 instancias x 10 = 60 conexiones, de un `max_connections` de 200 compartido con 3 servicios.

## Checklist de revisión
- [ ] `maximum-pool-size` explícito y justificado con instancias x pool.
- [ ] `connection-timeout` y `max-lifetime` fijados.
- [ ] No hay llamadas externas dentro de transacciones.
- [ ] Métricas del pool visibles.
- [ ] Batch y online no comparten pool sin decisión.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Conftest: `maximum-pool-size` ausente o > umbral en config | 1 | pendiente (`policies/opa-conftest/`) |
| Revisión de dimensionado | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `transactions`, `read-replicas-and-routing`, `multi-tenancy`, `actuator-and-health`.
- Fuentes: documentación de HikariCP (About Pool Sizing) y Spring Boot (Data Access).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
