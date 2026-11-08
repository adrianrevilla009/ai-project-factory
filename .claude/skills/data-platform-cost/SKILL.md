---
name: data-platform-cost
description: "Usar al dimensionar o revisar el coste de una plataforma de datos: almacenamiento, cómputo de consultas, ingesta, egress, particionado y formatos, con presupuestos y atribución por dominio."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Coste de la plataforma de datos

## Cuándo aplicar y cuándo no
- Aplica al elegir formato, particionado, motor de consulta, frecuencia de refresco y retención en lago/warehouse.
- No aplica al coste general de infraestructura (ver `cost-visibility`); aquí solo lo específico de datos.

## Reglas
- **MUST** etiquetar recursos y consultas por dominio/equipo para atribuir coste (tags de recurso, etiqueta de consulta o grupo de trabajo).
- **MUST** usar formatos columnares comprimidos (Parquet) y particionar por la columna de filtrado habitual; evitar millones de ficheros pequeños (compactar).
- **MUST** aplicar retención y ciclo de vida por zona: raw frío o expirado, gold caliente (ver `access-control-masking-and-retention`).
- **MUST** fijar un presupuesto y alerta por dominio; revisarlo mensualmente.
- **SHOULD** ajustar la frecuencia de refresco al valor de negocio (diario antes que cada minuto) y preferir cargas incrementales.
- **SHOULD** limitar `SELECT *` y escaneos sin filtro de partición; usar vistas agregadas para BI.
- **SHOULD** vigilar egress entre regiones y servicios; mantener cómputo y datos en la misma región.
- **MUST NOT** afirmar cifras de precio sin fuente y fecha: los precios del proveedor se comprueban en la página oficial en el momento de decidir.
- **MUST NOT** introducir un servicio de pago por defecto (D16); comparar primero con alternativas OSS.

## Por qué
En plataformas de datos el coste crece con los bytes escaneados y la frecuencia de refresco, no con el número de servidores. Particionado, formato y retención suelen reducir el escaneo de forma notable, y la atribución por dominio hace visible quién gasta. Las estimaciones se hacen con el calculador oficial del proveedor y quedan como "estimación, no verificada en real".

## Ejemplos
### Mal
```sql
-- tabla sin particionar, consulta de BI cada 5 minutos
SELECT * FROM gold.events WHERE event_date = DATE '2026-11-01';
```
### Bien
```sql
CREATE TABLE gold.events (
  event_id bigint, event_ts timestamp, event_date date, customer_id bigint
) USING iceberg
PARTITIONED BY (event_date);

-- consulta con poda de partición y columnas explícitas
SELECT event_id, customer_id FROM gold.events WHERE event_date = DATE '2026-11-01';
```
```yaml
# cost_budget.yml
- domain: sales-data
  monthly_budget_eur: 500        # ejemplo; fijar con el cliente
  alert_at_percent: [50, 80, 100]
  owner: "team-sales-data"
```

## Checklist de revisión
- [ ] Recursos y consultas etiquetados por dominio.
- [ ] Parquet/Iceberg con particionado acorde al filtro principal.
- [ ] Retención y compactación definidas.
- [ ] Presupuesto con alertas y dueño.
- [ ] Cifras de precio con fuente y fecha, o marcadas TODO-VERIFY.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de particionado, formatos y presupuesto en PR | 3 | agente `code-reviewer` |
| Regla Checkov/Conftest: buckets de datos sin ciclo de vida o recursos sin tag de dominio | 1 | pendiente (`policies/iac-checks/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cost-visibility`, `data-lake-and-lakehouse`, `warehouse-options`, `partitioning-and-archival`, `finops-of-resilience`.
- Fuentes: calculadora de precios oficial del proveedor (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
