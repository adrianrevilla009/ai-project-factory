---
name: cardinality-and-cost-governance
description: "Usar al añadir métricas, etiquetas o logs nuevos, o al investigar crecimiento de series y coste de observabilidad."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Cardinalidad y gobierno de costes

## Cuándo aplicar y cuándo no
- Aplica a métricas Micrometer/OTel nuevas, etiquetas de logs, atributos de spans y a revisiones de coste del almacenamiento.
- No aplica a la retención en sí (ver `metrics-store-ha-retention` y `logs-and-traces-stores`), aunque comparten presupuesto.

## Reglas
- **MUST** que ninguna etiqueta de métrica tome valores no acotados (ID de usuario, pedido, email, URL con parámetros, traceId).
- **MUST** usar la plantilla de ruta (`/orders/{id}`) y no la URL cruda como etiqueta `uri`.
- **MUST** presupuesto de series activas por servicio y tenant; superarlo bloquea el despliegue o dispara alerta.
- **MUST** límites duros en el scrape: `sample_limit`, `label_limit` y `label_value_length_limit` por job (confirmar nombres: TODO-VERIFY).
- **MUST** eliminar en origen lo no usado con `metric_relabel_configs` (`action: drop`) o en el Collector, antes de almacenar.
- **MUST** vigilar `prometheus_tsdb_head_series` y las top-N métricas por series con un dashboard y alerta de crecimiento.
- **SHOULD** buckets de histograma justificados; cada bucket multiplica series por las demás etiquetas.
- **SHOULD** muestreo de trazas (por cola, errores y latencia siempre) y niveles de log en producción `INFO`.
- **SHOULD** atribuir coste por tenant/equipo (showback) y revisarlo mensualmente.
- **MUST NOT** convertir en etiqueta lo que es un atributo de span o un campo de log.

## Por qué
El coste de una métrica es el producto de los valores de sus etiquetas. Una sola etiqueta con 100 000 valores multiplica memoria y disco de Prometheus. El control debe ser preventivo (límites y revisión) porque la factura llega después.

## Ejemplos
### Mal
```java
Counter.builder("orders.created").tag("userId", userId).tag("path", request.getRequestURI()).register(registry);
```
### Bien
```java
Counter.builder("orders.created").tag("channel", channel.name()).register(registry); // enum acotado
// userId y traceId van en el log estructurado y en el span, no como tag
```
```yaml
scrape_configs:
  - job_name: orders-api
    sample_limit: 50000
    label_limit: 30
    metric_relabel_configs:
      - source_labels: [__name__]
        regex: "go_gc_.*|jvm_buffer_.*"
        action: drop
```
```text
topk(10, count by (__name__) ({__name__=~".+"}))
```
La consulta anterior es costosa: ejecutarla bajo demanda, no en un dashboard.

## Checklist de revisión
- [ ] Todas las etiquetas nuevas tienen conjunto de valores acotado.
- [ ] `sample_limit`/`label_limit` en cada job.
- [ ] Métricas no usadas descartadas.
- [ ] Dashboard de series activas y alerta de crecimiento.
- [ ] Histogramas y muestreo justificados.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Regla Semgrep para tags de Micrometer con IDs (userId, orderId) | 1 | pendiente: `policies/semgrep/` |
| Regla Conftest: job de scrape sin `sample_limit` | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de métricas nuevas | 3 | agente revisor |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `metrics-store-ha-retention`, `logs-and-traces-stores`, `multi-tenant-observability`, `collector-pipelines`, `finops` (bloque 19).
- Fuentes oficiales: https://prometheus.io/docs/prometheus/latest/configuration/configuration/ (límites de scrape y `metric_relabel_configs`; no verificada en esta sesión (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
