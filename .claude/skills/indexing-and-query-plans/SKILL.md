---
name: indexing-and-query-plans
description: Usar al crear índices, diagnosticar consultas lentas o revisar planes de ejecución (EXPLAIN ANALYZE) en PostgreSQL.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Índices y planes de consulta (PostgreSQL)

## Cuándo aplicar y cuándo no
- Aplica a toda consulta nueva sobre tablas que puedan crecer, a índices nuevos y a diagnósticos de lentitud.
- No aplica a tablas diminutas y estables (catálogos de decenas de filas) ni a ajustes de parámetros del servidor (ámbito de operaciones/DBA).

## Reglas
- **MUST** indexar las columnas de claves foráneas usadas en joins/borrados (PostgreSQL no las indexa automáticamente).
- **MUST** diseñar índices desde las consultas reales: orden de columnas compuestas = igualdad primero, luego rango/orden.
- **MUST** revisar con `EXPLAIN (ANALYZE, BUFFERS)` sobre un volumen de datos realista las consultas críticas antes de aprobar; un Seq Scan sobre tabla grande necesita justificación.
- **MUST** respaldar cada índice con una consulta que lo use; los índices cuestan escrituras y espacio. Eliminar los no usados (`pg_stat_user_indexes`) tras observar un ciclo completo de carga.
- **MUST NOT** envolver la columna indexada en funciones (`lower(email) = ...`) sin un índice de expresión equivalente.
- **MUST NOT** fiarse del plan en una BD de desarrollo con 100 filas.
- **SHOULD** usar índices parciales (`WHERE deleted_at IS NULL`), de cobertura (`INCLUDE`) y GIN/BRIN donde encajen, justificándolo con un plan.
- **SHOULD** mantener estadísticas al día (autovacuum) y vigilar `pg_stat_statements` para detectar las consultas más costosas (TODO-VERIFY extensión disponible en el entorno).
- **SHOULD** crear índices con `CONCURRENTLY` (ver `schema-migrations`).

## Por qué
Una consulta sin índice adecuado funciona hasta que la tabla crece; entonces degrada todo el pool (ver `connection-pooling`). El optimizador decide según estadísticas y volumen: solo el plan real lo muestra. Demasiados índices frenan inserciones y actualizaciones. Verificar sintaxis y opciones de `EXPLAIN` contra la documentación de la versión de PostgreSQL usada (TODO-VERIFY).

## Ejemplos
### Mal
```sql
SELECT * FROM orders WHERE lower(customer_email) = 'ana@example.com';  -- Seq Scan
-- sin indice en orders.customer_id (FK)
```
### Bien
```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_created
  ON orders (customer_id, created_at DESC) WHERE deleted_at IS NULL;

CREATE INDEX CONCURRENTLY idx_orders_email_lower ON orders (lower(customer_email));

EXPLAIN (ANALYZE, BUFFERS)
SELECT id, total FROM orders
WHERE customer_id = '00000000-0000-0000-0000-000000000001' AND deleted_at IS NULL
ORDER BY created_at DESC LIMIT 20;
-- esperado: Index Scan sobre idx_orders_customer_created, sin Sort
```
`EXPLAIN ANALYZE` ejecuta la consulta: no usarlo con sentencias de escritura sin `BEGIN ... ROLLBACK`.

## Checklist de revisión
- [ ] Toda FK usada en joins tiene índice.
- [ ] El orden de columnas responde a la consulta real.
- [ ] Hay un plan (`EXPLAIN ANALYZE`) con datos realistas para las consultas críticas.
- [ ] No hay funciones sobre columnas indexadas sin índice de expresión.
- [ ] No hay índices duplicados o sin uso.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Comprobación de FKs sin índice en test de esquema | 1 | pendiente (tests del proyecto generado) |
| Revisión de planes en consultas nuevas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `schema-migrations`, `query-strategy`, `pagination`, `partitioning-and-archival`, `db-design-conventions`.
- Fuentes: documentación de PostgreSQL (Indexes, Using EXPLAIN) — TODO-VERIFY URL y versión; no verificado 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
