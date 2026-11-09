---
name: tempo-and-service-graphs
description: "Usar al habilitar el metrics-generator de Tempo (service graphs, span metrics) y al enlazar trazas con métricas y logs en Grafana."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Tempo, service graphs y métricas desde trazas

## Cuándo aplicar y cuándo no
- Aplica a la configuración del metrics-generator de Tempo y a la correlación traza/métrica/log en Grafana.
- No aplica al almacenamiento y retención de bloques de Tempo (ver `logs-and-traces-stores`) ni a la instrumentación de la aplicación.

## Reglas
- **MUST** habilitar el metrics-generator con los procesadores necesarios (`service-graphs`, `span-metrics`) y un `remote_write` a Prometheus; sin remote write las métricas generadas no se guardan.
- **MUST** que los spans lleven `service.name` consistente y atributos de peer/mensajería correctos; sin ellos el grafo de servicios queda incompleto o con nodos "desconocidos".
- **MUST** limitar las dimensiones de `span-metrics` a un conjunto acotado (p. ej. `http.method`, `http.route`); no usar atributos de alta cardinalidad (ver `cardinality-and-cost-governance`).
- **MUST** propagar el contexto W3C `traceparent` entre servicios, colas incluidas (cabeceras Kafka).
- **SHOULD** derivar RED (tasa, errores, duración) de span metrics para servicios sin métricas propias, pero preferir las métricas nativas de la aplicación para los SLOs.
- **SHOULD** exemplars en histogramas y datasource Grafana con "trace to logs" y "trace to metrics" configurados.
- **SHOULD** muestreo decidido en el gateway: el metrics-generator debe recibir spans antes de descartarlos si se quieren métricas sin sesgo.
- **MUST NOT** usar el service graph como fuente de verdad de arquitectura: es observado, no declarado.

## Por qué
El service graph da un mapa vivo de dependencias y tasas de error sin instrumentación extra, pero solo es útil si los nombres de servicio y la propagación de contexto son correctos. Las métricas derivadas se pueden disparar en coste si se añaden dimensiones libres.

## Ejemplos
### Mal
```yaml
metrics_generator:
  processor:
    span_metrics:
      dimensions: [user.id, http.url]   # cardinalidad no acotada
```
### Bien
```yaml
metrics_generator:
  processor:
    service_graphs: {}
    span_metrics:
      dimensions: [http.method, http.route]
  storage:
    path: /var/tempo/generator/wal
    remote_write:
      - url: http://prometheus.observability:9090/api/v1/write
overrides:
  defaults:
    metrics_generator:
      processors: [service-graphs, span-metrics]
```
```text
sum(rate(traces_service_graph_request_total{client="web", server="orders"}[5m]))
```
El nombre `traces_service_graph_request_total` es el habitual. Prometheus necesita `--web.enable-remote-write-receiver` para aceptar `/api/v1/write` (verificado en la documentación de Prometheus).

## Criterios de decisión y trampas
### Cómo decidir
- Trazas con un almacén barato por identificador y grafos de servicio generados desde las propias trazas; combina métricas derivadas de spans con cuidado de cardinalidad.
- Muestreo coherente en toda la cadena.
### Trampas frecuentes
- Esperar poder buscar por cualquier atributo sin índices.
- Métricas de spans con cardinalidad enorme.
- Muestreo distinto en cada servicio.
- Grafos que no reflejan dependencias reales por trazas rotas.
- Retención sin criterio.
### Evidencia
- Un grafo de servicios que coincide con las dependencias reales conocidas.

## Checklist de revisión
- [ ] Processors habilitados y remote write operativo.
- [ ] `service.name` consistente en todos los servicios.
- [ ] Dimensiones de span-metrics acotadas.
- [ ] Propagación `traceparent` en HTTP y mensajería.
- [ ] Enlaces trace-to-logs y trace-to-metrics en Grafana.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Regla Conftest sobre `span_metrics.dimensions` (lista permitida) | 1 | pendiente: `policies/opa-conftest/` |
| Revisión del grafo de servicios tras cada entrega | 3 | agente revisor |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `logs-and-traces-stores`, `collector-pipelines`, `cardinality-and-cost-governance`, `dashboards-and-slos-as-code`.
- Fuentes oficiales: https://grafana.com/docs/tempo/latest/metrics-from-traces/metrics-generator/ (verificado 2026-11-07: procesadores service graphs, span metrics y host info; los nombres de métricas y la sintaxis de overrides no aparecieron en esa página. https://prometheus.io/docs/prometheus/latest/storage/ (receptor de remote write).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
