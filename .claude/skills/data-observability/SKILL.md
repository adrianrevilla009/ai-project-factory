---
name: data-observability
description: "Usar al monitorizar pipelines y datasets en producción: frescura, volumen, esquema, distribución, linaje y alertas con SLO, para detectar datos rotos antes que el negocio."
metadata:
  block: "23-data-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Observabilidad de datos

## Cuándo aplicar y cuándo no
- Aplica a pipelines batch/streaming y datasets de gold que alimentan BI, ML o integraciones.
- No aplica a la observabilidad de servicios (métricas/trazas de apps); para eso ver `collector-pipelines` y `slo-error-budget-policy`.

## Reglas
- **MUST** monitorizar por dataset crítico cinco señales: frescura, volumen, esquema, distribución/valores nulos y fallos de tests de calidad.
- **MUST** declarar un SLO por dataset crítico (p. ej. "gold.fct_orders actualizado antes de las 07:00") con dueño y canal de aviso.
- **MUST** emitir métricas del pipeline (duración, filas leídas/escritas, reintentos) con identificador de ejecución, y enlazarlas al linaje (OpenLineage,).
- **MUST** enrutar alertas al dueño del dataset, no a un canal genérico; cada alerta enlaza un runbook.
- **SHOULD** usar umbrales basados en histórico (estacionalidad) en lugar de valores fijos para volumen.
- **SHOULD** exponer el estado de datos como metadatos consultables (tabla `dataset_health`).
- **MUST NOT** incluir valores de datos personales en métricas, logs o alertas; solo contadores y agregados.
- **MUST NOT** tratar un pipeline en verde como prueba de datos correctos: puede escribir cero filas con éxito.

## Por qué
Los fallos de datos son silenciosos: el job termina bien y el informe del lunes es erróneo. Medir frescura y volumen detecta el 80 % de los casos sin lógica de negocio; el linaje acota el radio de impacto aguas abajo.

## Ejemplos
### Mal
```python
def run():
    df = load()
    df.write.mode("overwrite").saveAsTable("gold.fct_orders")  # éxito aunque df esté vacío
```
### Bien
```python
def run(ctx):
    df = load()
    rows = df.count()
    if rows == 0 or rows < 0.5 * ctx.avg_rows_last_7d("gold.fct_orders"):
        raise DataVolumeAnomaly(f"rows={rows}")   # sin valores de datos en el mensaje
    df.write.mode("overwrite").saveAsTable("gold.fct_orders")
    ctx.emit_metrics(dataset="gold.fct_orders", rows=rows, run_id=ctx.run_id)
```
```yaml
# dataset_slo.yml
- dataset: gold.fct_orders
  freshness_max_minutes: 120
  owner: "team-sales-data"
  runbook: "runbooks/fct-orders-late.md"
```

## Checklist de revisión
- [ ] Cada dataset crítico tiene SLO, dueño y runbook.
- [ ] Hay chequeo de frescura y volumen que falla el pipeline o alerta.
- [ ] Las alertas no contienen datos personales.
- [ ] El linaje identifica consumidores afectados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana de SLOs y chequeos de pipeline | 3 | agente `code-reviewer` |
| Regla Conftest que exige `owner` y `runbook` en `dataset_slo.yml` | 1 | pendiente (`policies/opa-conftest/`) |
| Test de pipeline con entrada vacía que debe fallar | 1 | pendiente, proyecto generado |

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-quality`, `data-contracts-and-lineage`, `batch-orchestration`, `alert-routing-and-oncall`, `slo-error-budget-policy`.
- Fuentes: especificación OpenLineage (openlineage.io).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
