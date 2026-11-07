---
name: golden-signals-red-use
description: "Usar al diseñar dashboards y métricas base de un servicio: golden signals, método RED para servicios y USE para recursos."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Golden signals, RED y USE

## Cuándo aplicar y cuándo no
- Aplica al definir el dashboard mínimo de cada servicio y a la elección de qué métricas son imprescindibles.
- No aplica a métricas de negocio específicas ni a la política de alertas (ver `alerting-symptom-based`).

## Reglas
- **MUST** cubrir para cada servicio expuesto las señales RED: tasa de peticiones (Rate), errores (Errors) y duración (Duration) por endpoint (`http.route`, no URL cruda).
- **MUST** cubrir para cada recurso (CPU, memoria, pool de conexiones, cola, disco) el método USE: utilización, saturación y errores.
- **MUST** añadir saturación (colas, pool pendiente, lag) como cuarta señal dorada.
- **MUST** medir la latencia con histograma y mostrar percentiles (p50/p95/p99) calculados con `histogram_quantile`; **MUST NOT** promediar percentiles entre instancias.
- **MUST** separar errores de servidor (5xx, excepciones) de rechazos de cliente (4xx).
- **SHOULD** versionar los dashboards como código (JSON/Grafonnet/provisioning) con la misma plantilla para todos los servicios.
- **SHOULD** ordenar el dashboard de arriba abajo: SLO y RED, dependencias, recursos USE, JVM.
- **MUST NOT** crear un dashboard sin dueño ni enlace a su runbook.

## Por qué
Un conjunto pequeño y común de señales permite que cualquiera en guardia entienda cualquier servicio. RED responde "¿el usuario sufre?", USE responde "¿qué recurso lo causa?". Los promedios ocultan la cola de latencia que sufren los usuarios.

## Ejemplos
### Mal
```promql
avg(http_server_requests_seconds_sum / http_server_requests_seconds_count)
```
### Bien
```promql
# Rate
sum by (uri) (rate(http_server_requests_seconds_count{application="orders-api"}[5m]))
# Errors (ratio 5xx)
sum(rate(http_server_requests_seconds_count{application="orders-api",status=~"5.."}[5m]))
  / sum(rate(http_server_requests_seconds_count{application="orders-api"}[5m]))
# Duration p95 (requiere histograma activado)
histogram_quantile(0.95,
  sum by (le) (rate(http_server_requests_seconds_bucket{application="orders-api"}[5m])))
# Saturación del pool
max(hikaricp_connections_pending{application="orders-api"})
```
Los nombres de métrica dependen del exportador y la versión de Micrometer (TODO-VERIFY).

## Checklist de revisión
- [ ] RED por endpoint y USE por recurso presentes.
- [ ] Latencia con histograma y percentiles.
- [ ] 4xx y 5xx separados.
- [ ] Dashboard como código con dueño y enlace a runbook.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de dashboards como código | 3 | agente `code-reviewer` |
| Validador de plantilla de dashboard (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `metrics-micrometer`, `jvm-observability`, `alerting-symptom-based`, `slo-sli-error-budgets`, `on-call-and-runbook-links`.
- Fuentes: libro SRE de Google (golden signals), método RED (Tom Wilkie) y USE (Brendan Gregg), consultados 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
