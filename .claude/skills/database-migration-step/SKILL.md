---
name: database-migration-step
description: "Usar al decidir cómo y cuándo se ejecutan las migraciones de base de datos dentro del pipeline de despliegue."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Paso de migración de base de datos en el pipeline

## Cuándo aplicar y cuándo no
- Aplica a servicios con Flyway (ver `schema-migrations`) desplegados con rolling o canary.
- No aplica al diseño de la migración (expand/contract) ni a NoSQL sin esquema versionado.

## Reglas
- **MUST** ejecutar la migración como paso explícito y previo al despliegue de la aplicación (job o Kubernetes Job), no al arrancar N réplicas a la vez.
- **MUST** que la migración sea compatible con la versión anterior de la app (expand/contract): la app N-1 debe funcionar con el esquema N.
- **MUST** probar la migración en CI contra una BD real (Testcontainers) con datos representativos, y validar `flyway validate`/checksums.
- **MUST** que la migración use un usuario con DDL distinto del usuario de runtime (mínimo privilegio).
- **MUST** hacer backup o punto de restauración verificable antes de migraciones destructivas en entornos no efímeros.
- **MUST NOT** editar migraciones ya aplicadas; se corrige con una nueva versión.
- **MUST NOT** usar `flyway clean` ni `baselineOnMigrate` fuera de entornos efímeros.
- **SHOULD** fijar `lock_timeout` y ejecutar índices con `CONCURRENTLY` en PostgreSQL.

## Por qué
Con rolling deploy conviven dos versiones de la app; un `DROP COLUMN` rompe a la anterior. Migrar en N pods compite por el bloqueo y mezcla el fallo de migración con el de arranque. El rollback de esquema casi nunca es posible: se diseña hacia adelante (`rollback-strategy`).

## Ejemplos
### Mal
```yaml
spring.flyway.clean-disabled: false
spring.flyway.baseline-on-migrate: true
```
```sql
ALTER TABLE orders DROP COLUMN legacy_status;
```
### Bien
```yaml
migrate:
  runs-on: ubuntu-latest
  environment: staging
  steps:
    - run: >
        ./mvnw -B flyway:migrate -Dflyway.url=$DB_URL
        -Dflyway.user=$MIGRATOR_USER -Dflyway.password=$MIGRATOR_PASSWORD
  # credenciales del entorno (example/changeme solo en local); plugin y flags
deploy:
  needs: migrate
```
```sql
-- V12__expand_orders_status.sql (fase expand; el DROP va en una versión posterior)
SET lock_timeout = '5s';
ALTER TABLE orders ADD COLUMN status_code smallint;
```

## Criterios de decisión y trampas
### Cómo decidir
- Expand/contract: la migración de esta versión es compatible con el código de la anterior; así el despliegue progresivo y el rollback son seguros.
- Una migración como paso explícito antes del despliegue, no al arrancar la aplicación con varias réplicas.
- Cambios grandes (reescrituras de tablas): en lotes y con la aplicación aún compatible.
### Trampas frecuentes
- Migraciones destructivas en el mismo despliegue que el código que las necesita.
- Que cada réplica intente migrar al arrancar.
- Usuario de runtime con permisos de DDL.
- Migraciones que bloquean tablas grandes sin planificar la ventana.
- Editar una migración ya aplicada.
### Evidencia
- La migración se probó en CI contra una base real con datos representativos y se documentó su reversión o su compensación.

## Checklist de revisión
- [ ] Migración como paso previo único, no en el arranque de N pods.
- [ ] Compatible con N-1 (expand/contract).
- [ ] Probada en CI con Testcontainers.
- [ ] Usuario de migración separado del de runtime.
- [ ] Sin `clean` ni `baselineOnMigrate` fuera de efímeros.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: DROP/RENAME COLUMN e índices sin CONCURRENTLY | 1 | `policies/semgrep/sql-unsafe-migrations.yaml` |
| Regla Rego: `clean-disabled: false` / `baseline-on-migrate` en config | 1 | pendiente |
| Revisión de la migración y el backup previo | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `schema-migrations`, `rollback-strategy`, `deployment-verification-and-smoke`, `db-testing`.
- Fuentes: documentación de Flyway (https://documentation.red-gate.com/flyway).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
