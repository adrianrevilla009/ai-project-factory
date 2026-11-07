---
name: collector-pipelines
description: "Usar al definir o revisar pipelines del OpenTelemetry Collector (receivers, processors, exporters) que alimentan Prometheus, Loki y Tempo."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Pipelines del OpenTelemetry Collector

## Cuándo aplicar y cuándo no
- Aplica a cualquier `otel-collector` config (agente por nodo o gateway) en la plataforma D22 (OTel + Prometheus + Grafana + Loki + Tempo).
- No aplica a la instrumentación dentro de la app Java (ver skills de logging/tracing de la app) ni a la configuración interna de Loki/Tempo.

## Reglas
- **MUST** declarar `memory_limiter` como primer processor y `batch` como último en cada pipeline; el orden de `processors` es el orden de ejecución.
- **MUST** separar dos capas: agente (DaemonSet, receivers OTLP locales, enriquecimiento k8s) y gateway (Deployment, muestreo, enrutado por tenant, exportación).
- **MUST** definir un pipeline por señal (`traces`, `metrics`, `logs`) y variantes con `type/name` (`traces/errors`) en lugar de un único pipeline con condiciones.
- **MUST** habilitar la extensión `health_check` y usarla en liveness/readiness.
- **MUST NOT** hacer tail sampling en el agente: necesita todos los spans de una traza en la misma réplica; usar gateway con balanceo por `traceID` (TODO-VERIFY exporter `loadbalancing` en la distribución contrib usada).
- **MUST NOT** exportar sin cola/reintentos configurados ni sin límite de memoria (el Collector es un punto único de pérdida de telemetría).
- **SHOULD** usar la distribución contrib solo si hacen falta componentes contrib; mejor construir una distribución mínima con `ocb` (OpenTelemetry Collector Builder) fijando versiones.
- **SHOULD** exportar a Tempo y Loki por OTLP y a Prometheus por remote write o scrape del endpoint del Collector.
- **MUST NOT** poner tokens o contraseñas en el YAML: usar variables de entorno `${env:NAME}` alimentadas desde Secret.

## Por qué
Sin `memory_limiter` un pico de telemetría tumba el Collector y se pierde justo la señal del incidente. El orden de processors cambia el resultado (batch antes de limitar memoria no protege). Separar agente y gateway permite escalar el muestreo sin tocar cada nodo.

## Ejemplos
### Mal
```yaml
service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]            # sin memory_limiter
      exporters: [otlp/tempo]
exporters:
  otlp/tempo:
    endpoint: tempo:4317
    headers: { authorization: "Bearer abc123-real-looking" }   # secreto en claro
```
### Bien
```yaml
extensions:
  health_check: {}
receivers:
  otlp:
    protocols: { grpc: {}, http: {} }
processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 20 }
  batch: {}
exporters:
  otlp/tempo:
    endpoint: tempo-distributor.observability:4317
    headers: { authorization: "Bearer ${env:TEMPO_TOKEN}" }   # TEMPO_TOKEN=changeme en local
service:
  extensions: [health_check]
  pipelines:
    traces:  { receivers: [otlp], processors: [memory_limiter, batch], exporters: [otlp/tempo] }
    metrics: { receivers: [otlp], processors: [memory_limiter, batch], exporters: [prometheusremotewrite] }
    logs:    { receivers: [otlp], processors: [memory_limiter, batch], exporters: [otlphttp/loki] }
```
(Los exporters `prometheusremotewrite` y `otlphttp/loki` se omiten por brevedad; nombres de componentes: TODO-VERIFY contra el registro de componentes.)

## Checklist de revisión
- [ ] `memory_limiter` primero y `batch` último en todos los pipelines.
- [ ] `health_check` habilitado y referenciado en las probes.
- [ ] Tail sampling solo en gateway con balanceo por traza.
- [ ] Sin secretos literales; versión del Collector fijada.
- [ ] Agente y gateway diferenciados.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Conftest que exige `memory_limiter` en cada pipeline | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de la config del Collector | 3 | agente revisor de infraestructura |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `metrics-store-ha-retention`, `logs-and-traces-stores`, `multi-tenant-observability`, `cardinality-and-cost-governance`.
- Fuentes oficiales: https://opentelemetry.io/docs/collector/configuration/ (verificado 2026-11-07; confirma pipelines en `service.pipelines`, orden de processors y extensiones). Valores de `memory_limiter`: TODO-VERIFY en docs del componente.
- Preparado para AWS, no verificado en real; en local se usa un único Collector sin la capa agente/gateway completa.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
