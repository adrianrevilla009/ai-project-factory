---
name: otel-fundamentals-and-semconv
description: "Usar al diseñar o revisar la telemetría de un servicio con OpenTelemetry: señales, Resource, convenciones semánticas, Collector y OTLP."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# OpenTelemetry: fundamentos y convenciones semánticas

## Cuándo aplicar y cuándo no
- Aplica a cualquier servicio que emita trazas, métricas o logs, y a la configuración del Collector (ADR-0022: OTel + Prometheus + Grafana + Loki + Tempo).
- No aplica a la elección agente vs SDK (ver `otel-java-agent-vs-sdk`) ni al detalle de cada señal (`metrics-micrometer`, `tracing`, `structured-logging`).

## Reglas
- **MUST** definir el `Resource` en cada servicio: `service.name`, `service.version`, `deployment.environment.name` (nombre vigente del atributo) y `service.namespace`.
- **MUST** usar nombres de atributo de las convenciones semánticas (`http.request.method`, `http.response.status_code`, `http.route`, `server.address`) en lugar de nombres propios.
- **MUST** exportar por OTLP al Collector, no directamente a cada backend; el Collector aplica `memory_limiter`, `batch`, redacción y enrutado.
- **MUST NOT** usar identificadores no acotados (userId, orderId, URL completa) como atributo de métrica; sí pueden ir en spans y logs.
- **MUST NOT** poner datos personales, tokens ni cuerpos completos en atributos de span.
- **SHOULD** prefijar atributos propios con el dominio (`acme.order.channel`) para no colisionar con semconv.
- **SHOULD** correlacionar las tres señales por `trace_id`/`span_id` y por los mismos atributos de Resource.
- **SHOULD** versionar la configuración del Collector en el repo del servicio o de plataforma (observabilidad como código).

## Por qué
Con nombres estándar, los dashboards, alertas y consultas son reutilizables entre servicios y entre backends. El Collector desacopla la aplicación del almacenamiento: cambiar Tempo o Loki no obliga a redeplegar servicios. La cardinalidad en métricas es el fallo de coste más común. Las convenciones semánticas evolucionan (algunas aún experimentales): fijar la versión usada y revisarla al actualizar.

## Ejemplos
### Mal
```yaml
# variables del servicio: sin Resource útil, exporta directo al backend
OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo.example.internal:4317
```
```java
counter.tag("user_id", userId).increment();   // cardinalidad ilimitada
span.setAttribute("customer.email", email);   // dato personal
```
### Bien
```yaml
OTEL_SERVICE_NAME: orders-api
OTEL_RESOURCE_ATTRIBUTES: service.namespace=shop,service.version=1.4.2,deployment.environment.name=staging
OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector.observability:4317
```
```yaml
# Collector (fragmento)
processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 20 }
  batch: {}
service:
  pipelines:
    traces: { receivers: [otlp], processors: [memory_limiter, batch], exporters: [otlp/tempo] }
```

## Criterios de decisión y trampas
### Cómo decidir
- Instrumenta con el estándar abierto y sus convenciones de nombres; así puedes cambiar de backend sin reinstrumentar.
- Pocos atributos útiles y estables mejor que muchos inconsistentes.
### Trampas frecuentes
- Nombres de atributos propios para lo que el estándar ya define.
- Atributos de cardinalidad ilimitada en métricas.
- Datos personales en atributos.
- Instrumentar todo sin saber qué se usará.
- Mezclar versiones de convenciones sin plan.
### Evidencia
- Un catálogo de atributos y métricas con propietario y revisión en cada cambio.

## Checklist de revisión
- [ ] `service.name`, versión y entorno definidos.
- [ ] Atributos con nombres semconv; propios con prefijo de dominio.
- [ ] Sin IDs de alta cardinalidad ni PII en métricas/atributos.
- [ ] Servicios exportan al Collector; este tiene `memory_limiter`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de atributos y config del Collector | 3 | agente `code-reviewer` |
| Regla de lint para el Collector (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `otel-java-agent-vs-sdk`, `metrics-micrometer`, `tracing`, `structured-logging`, `pii-and-data-classification`.
- Fuentes: documentación oficial de OpenTelemetry (opentelemetry.io: semantic conventions, Collector); versiones. En local se reproduce el stack OSS; no se reproducen servicios gestionados de AWS.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
