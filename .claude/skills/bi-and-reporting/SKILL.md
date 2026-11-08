---
name: bi-and-reporting
description: "Usar al elegir herramienta BI, diseñar capa semántica, dashboards y reportes sobre el warehouse, incluyendo permisos, rendimiento y definiciones únicas de métricas."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# BI y reporting

## Cuándo aplicar y cuándo no
- Aplica a dashboards, reportes programados y capa semántica de métricas sobre marts/warehouse.
- No aplica a generación de documentos operativos (facturas, PDFs transaccionales): ver `document-and-report-generation`.

## Reglas
- **MUST** definir cada métrica una sola vez (capa semántica o modelo gold) y reutilizarla; el dashboard no recalcula negocio.
- **MUST** conectar el BI a gold/marts con una cuenta de servicio de solo lectura, nunca a raw ni a la BD transaccional.
- **MUST** propagar o respetar la clasificación: dashboards con datos `restricted` solo para roles autorizados y sin exportación libre.
- **MUST** documentar por métrica: definición, dueño, granularidad y fuente.
- **SHOULD** preferir herramientas OSS por defecto (Apache Superset o Metabase OSS, comprobar licencia/versión); Power BI, Tableau u otros de pago solo si el cliente ya los tiene (D16).
- **SHOULD** agregar previamente (tablas resumen) en lugar de consultas pesadas sobre hechos.
- **SHOULD** versionar la definición de dashboards (export YAML/JSON) en Git.
- **MUST NOT** incrustar credenciales de BD en el dashboard ni en el repo.

## Por qué
Dos dashboards con "ingresos" distintos destruyen la confianza más rápido que cualquier caída. Una definición única más lectura sobre gold hace los números auditables y los permisos coherentes con el gobierno del dato.

## Ejemplos
### Mal
```sql
-- dentro del dashboard, sobre silver
SELECT SUM(amount * 0.79) AS revenue FROM silver.orders WHERE status <> 'x';
```
### Bien
```yaml
# metrics/revenue.yml (capa semántica o dbt metrics; comprobar herramienta)
metric: revenue_net
owner: "team-finance-data"
grain: "day"
source: gold.fct_orders
expression: "SUM(net_amount)"
filters: ["status = 'completed'"]
classification: internal
```
```sql
-- conexión BI: rol de solo lectura sobre gold
GRANT SELECT ON ALL TABLES IN SCHEMA gold TO bi_reader;
-- password: changeme-example (en producción, desde Vault; nunca en el repo)
```

## Checklist de revisión
- [ ] Cada métrica tiene definición única y dueño.
- [ ] El BI lee solo gold con rol de solo lectura.
- [ ] Dashboards sensibles restringidos a roles.
- [ ] Definiciones versionadas en Git.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de PR de métricas y exports de dashboards | 3 | agente `code-reviewer` |
| Escaneo de secretos en el repo | 1 | hooks de seguridad de la fábrica (`.claude/hooks/`) |
| Test que valida que el rol BI no tiene acceso a raw/silver | 1 | pendiente, proyecto generado |

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-modeling`, `warehouse-options`, `data-governance-and-classification`, `access-control-masking-and-retention`.
- Fuentes: documentación oficial de Superset/Metabase (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
