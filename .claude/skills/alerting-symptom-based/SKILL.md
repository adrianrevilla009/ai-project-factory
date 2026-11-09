---
name: alerting-symptom-based
description: "Usar al escribir o revisar alertas Prometheus/Alertmanager: alertar por síntomas del usuario, severidades, ruido, burn rate y enrutado."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Alertas basadas en síntomas

## Cuándo aplicar y cuándo no
- Aplica a reglas de alerta, rutas de Alertmanager y política de paginación.
- No aplica a dashboards de diagnóstico (ver `golden-signals-red-use`) ni a la definición de SLO (`slo-sli-error-budgets`).

## Reglas
- **MUST** paginar solo por síntomas que afectan al usuario (errores, latencia, indisponibilidad, frescura de datos) o por consumo de presupuesto de error; las causas (CPU, heap, un pod caído) van a paneles o tickets.
- **MUST** que toda alerta paginable sea accionable, urgente y esté documentada: `summary`, `description` y `runbook_url` obligatorios.
- **MUST** definir `severity` con valores cerrados (`page`, `ticket`, `info`) y enrutar solo `page` a la guardia.
- **MUST** usar `for:` o ventanas multi-ventana para evitar flapping; **MUST NOT** alertar con `for: 0m` sobre métricas ruidosas.
- **SHOULD** usar alertas de burn rate multi-ventana sobre SLO (rápida y lenta) en vez de umbrales fijos de error.
- **SHOULD** agrupar e inhibir en Alertmanager (una caída de dependencia no debe disparar 30 alertas).
- **MUST** incluir una alerta de "latido" (watchdog) para detectar que el pipeline de alertas sigue vivo.
- **MUST** revisar trimestralmente las alertas que más disparan o que nunca actuaron; eliminar o degradar las ruidosas.
- **MUST NOT** enviar secretos ni datos personales en las anotaciones.

## Por qué
Una guardia que recibe ruido deja de reaccionar. Los síntomas capturan fallos que no previste; las causas solo los que ya conoces. Un enlace al runbook reduce el tiempo de diagnóstico a las 3 a. m.

## Ejemplos
### Mal
```yaml
- alert: HighCPU
  expr: container_cpu_usage_seconds_total > 0.8
  labels: { severity: page }
```
### Bien
```yaml
groups:
- name: orders-api-slo
  rules:
  - alert: OrdersApiErrorBudgetFastBurn
    expr: |
      (sum(rate(http_server_requests_seconds_count{application="orders-api",status=~"5.."}[5m]))
        / sum(rate(http_server_requests_seconds_count{application="orders-api"}[5m])) > (14.4 * 0.001))
      and
      (sum(rate(http_server_requests_seconds_count{application="orders-api",status=~"5.."}[1h]))
        / sum(rate(http_server_requests_seconds_count{application="orders-api"}[1h])) > (14.4 * 0.001))
    for: 2m
    labels: { severity: page, team: orders }
    annotations:
      summary: "orders-api consume el presupuesto de error muy rápido"
      runbook_url: "https://runbooks.example.internal/orders-api/error-budget"
```
Factor 14.4 y SLO 99.9 % son ilustrativos; calcular según el SLO real.

## Checklist de revisión
- [ ] Toda alerta `page` es síntoma o burn rate.
- [ ] `runbook_url`, `summary` y `severity` presentes.
- [ ] `for:`/multi-ventana definidos; agrupación e inhibición configuradas.
- [ ] Existe alerta watchdog.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: alertas `page` sin `runbook_url` (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |
| Revisión de reglas de alerta | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `slo-sli-error-budgets`, `golden-signals-red-use`, `on-call-and-runbook-links`, `jvm-observability`.
- Fuentes: documentación de Prometheus Alertmanager y The Site Reliability Workbook (alerting on SLOs), consultados 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
