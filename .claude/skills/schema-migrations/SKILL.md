---
name: schema-migrations
description: Usar al crear o revisar migraciones de esquema con Flyway y al planificar cambios compatibles hacia atrás (expand/contract).
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Migraciones de esquema (Flyway, expand/contract)

## Cuándo aplicar y cuándo no
- Aplica a todo cambio de DDL o de datos de referencia en BD relacionales gestionadas por el servicio.
- No aplica a datos de prueba (ver `db-testing`) ni a migraciones de datos masivas entre sistemas.

## Reglas
- **MUST** gestionar el esquema solo con migraciones versionadas Flyway (`V<n>__descripcion.sql`) en el repo; `spring.jpa.hibernate.ddl-auto` en `none` o `validate`, nunca `update`/`create` fuera de tests efímeros.
- **MUST NOT** editar una migración ya aplicada en cualquier entorno compartido; corregir con una nueva versión (Flyway valida checksums).
- **MUST** aplicar expand/contract para cambios incompatibles: (1) expandir con columna/tabla nueva nullable, (2) desplegar código que escribe en ambos y lee de la nueva, (3) rellenar datos por lotes, (4) contraer en un release posterior.
- **MUST** que cada versión de la aplicación funcione con el esquema anterior y el siguiente (rolling deploy): no renombrar ni borrar columnas en el mismo release que deja de usarlas.
- **MUST** evitar bloqueos largos: `CREATE INDEX CONCURRENTLY` en PostgreSQL (fuera de transacción), añadir `NOT NULL`/FK en dos pasos (`NOT VALID` + `VALIDATE`), `lock_timeout` en la migración.
- **MUST NOT** mezclar DDL pesado y backfill masivo en una sola migración; el backfill va por lotes y reanudable.
- **SHOULD** una migración por cambio lógico, idempotente en su intención y revisada junto al código.
- **SHOULD** probar migraciones contra PostgreSQL real (Testcontainers) desde un esquema vacío y desde una copia de la versión anterior.
- **SHOULD** no depender de migraciones "undo" (de pago en Flyway Teams); el plan de vuelta atrás es avanzar con otra migración.

## Por qué
El esquema es estado compartido entre versiones de la aplicación durante un despliegue gradual. Un `DROP COLUMN` o `RENAME` en un paso rompe las instancias antiguas. Un `CREATE INDEX` normal bloquea escrituras. Verificar sintaxis y comportamiento en documentación oficial de Flyway y PostgreSQL de la versión usada. Aquí no se afirma nada de ejecución en AWS real: preparado para AWS (p. ej. RDS), no verificado en real.

## Ejemplos
### Mal
```sql
-- V7__rename.sql: rompe instancias antiguas durante el rolling deploy
ALTER TABLE customer RENAME COLUMN phone TO phone_number;
CREATE INDEX idx_orders_customer ON orders (customer_id);   -- bloquea escrituras
```
### Bien
```sql
-- V7__add_phone_number.sql (expand)
ALTER TABLE customer ADD COLUMN phone_number text;

-- V8__idx_orders_customer.sql   (con flyway: executeInTransaction=false en su.conf)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_customer ON orders (customer_id);

-- V9__phone_not_null.sql (tras backfill y release que escribe la nueva columna)
ALTER TABLE customer ADD CONSTRAINT chk_phone_nn CHECK (phone_number IS NOT NULL) NOT VALID;
ALTER TABLE customer VALIDATE CONSTRAINT chk_phone_nn;
```
```yaml
spring:
  jpa:
    hibernate:
      ddl-auto: validate
  flyway:
    enabled: true
```

## Checklist de revisión
- [ ] Solo migraciones Flyway; `ddl-auto` es `none`/`validate`.
- [ ] Ninguna migración aplicada fue modificada.
- [ ] Cambios incompatibles divididos en expand/backfill/contract en releases distintos.
- [ ] Índices con `CONCURRENTLY`, constraints con `NOT VALID` + `VALIDATE`.
- [ ] Migración probada desde vacío y desde la versión previa.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep (SQL): `DROP COLUMN`/`RENAME COLUMN`/`CREATE INDEX` sin `CONCURRENTLY` en `db/migration` | 1 | `policies/semgrep/sql-unsafe-migrations.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Test de migración con Testcontainers (lo incluye el proyecto generado) | 1 | tests del proyecto generado |
| Revisión de migraciones | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `db-design-conventions`, `indexing-and-query-plans`, `db-testing`, `partitioning-and-archival`.
- Fuentes: documentación de Flyway y de PostgreSQL (CREATE INDEX, ALTER TABLE).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
