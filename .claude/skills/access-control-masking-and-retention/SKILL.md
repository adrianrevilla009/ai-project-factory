---
name: access-control-masking-and-retention
description: "Usar al definir quién lee qué en el lago o warehouse: roles, enmascarado de columnas, seguridad por fila y políticas de retención/borrado de datasets."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Control de acceso, enmascarado y retención en la plataforma de datos

## Cuándo aplicar y cuándo no
- Aplica a zonas del lago (raw/silver/gold), warehouse, marts y exportaciones a BI o ML.
- No aplica al RBAC de servicios de aplicación (ver `authz-rbac-abac-rebac`).

## Reglas
- **MUST** conceder acceso a roles (grupos del IdP), nunca a usuarios individuales; mínimo privilegio por zona.
- **MUST** restringir raw a la plataforma de datos; analistas leen solo silver/gold.
- **MUST** enmascarar o seudonimizar columnas `restricted`/`pii` por defecto en gold; el dato claro requiere rol explícito y registro de acceso.
- **MUST** definir retención por dataset (`retention_days`) y automatizar su aplicación (TTL, particiones, ciclo de vida).
- **MUST NOT** copiar datos clasificados a hojas de cálculo, buckets personales o entornos de desarrollo.
- **MUST NOT** usar datos de producción sin enmascarar en entornos no productivos.
- **SHOULD** aplicar seguridad por fila (row filter) para datos multi-tenant o regionales.
- **SHOULD** usar hash con sal gestionada (HMAC) para claves seudonimizadas que deban poder unirse entre tablas.

## Por qué
La mayoría de fugas analíticas vienen de copias y accesos excesivos, no de ataques. Enmascarar por defecto invierte la carga: pedir el dato claro es la excepción y queda auditada. La retención sin automatizar se incumple.
En local (Trino/Postgres/MinIO) se reproduce SQL de vistas y roles; NO se reproduce Lake Formation ni IAM de AWS: allí el diseño es "preparado para AWS, no verificado en real".

## Ejemplos
### Mal
```sql
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO jane_doe_example;
CREATE VIEW gold.customers AS SELECT * FROM silver.customers;
```
### Bien
```sql
CREATE ROLE analyst;
GRANT USAGE ON SCHEMA gold TO analyst;

CREATE VIEW gold.customers_masked AS
SELECT customer_id,
       md5(email) AS email_hash,          -- seudónimo; ver nota de sal
       country_code,
       signup_date
FROM silver.customers
WHERE country_code IN ('ES','PT');        -- filtro por fila de ejemplo

GRANT SELECT ON gold.customers_masked TO analyst;
```
```yaml
# retention.yml (por dataset)
- dataset: silver.customers
  retention_days: 1095
  action: delete_partitions
```
Nota: `md5` sin sal es reversible por diccionario; usar HMAC con secreto de Vault en producción.

## Checklist de revisión
- [ ] Los permisos van a roles, no a personas.
- [ ] Gold no expone columnas `pii` en claro por defecto.
- [ ] Cada dataset tiene retención y un mecanismo que la aplica.
- [ ] Dev/test usan datos sintéticos o enmascarados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Conftest: grants a usuarios individuales en IaC/SQL | 1 | pendiente (`policies/opa-conftest/`) |
| Test del proyecto que consulta gold con rol analyst y falla si ve columnas `pii` | 1 | pendiente, proyecto generado |
| Revisión de vistas y retención | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-governance-and-classification`, `gdpr-in-the-lake`, `retention-and-cleanup`, `data-privacy-in-db`, `secrets-management`.
- Fuentes: documentación de Trino (control de acceso).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
