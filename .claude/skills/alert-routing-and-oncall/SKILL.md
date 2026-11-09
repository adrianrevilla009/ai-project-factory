---
name: alert-routing-and-oncall
description: "Usar al escribir reglas de alerta de Prometheus y configurar Alertmanager: severidades, agrupación, inhibición y guardia."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Enrutado de alertas y guardia

## Cuándo aplicar y cuándo no
- Aplica a reglas de alerta, config de Alertmanager y rotación de guardia.
- No aplica a la definición de SLOs (ver `dashboards-and-slos-as-code`) ni a la comunicación a clientes (ver `status-page-and-comms`).

## Reglas
- **MUST** que toda alerta que despierte a una persona sea accionable, urgente y con `runbook_url` en anotaciones; el resto va a ticket o dashboard.
- **MUST** usar dos niveles de severidad como mínimo (`critical` page, `warning` ticket) y rutear por `matchers` sobre `severity` y `team`.
- **MUST** definir `group_by` (p. ej. `[cluster, alertname, namespace]`), `group_wait`, `group_interval` y `repeat_interval` explícitos.
- **MUST** `inhibit_rules` para suprimir síntomas cuando existe la causa (p. ej. `warning` si hay `critical` con el mismo `instance`/`service`).
- **MUST** alertar sobre síntomas (burn rate de SLO, errores, latencia) y no sobre causas (CPU alta) salvo capacidad.
- **MUST** una alerta "watchdog" siempre activa hacia un monitor externo que avise si la cadena de alertado cae.
- **SHOULD** un receiver por equipo; secretos de webhooks fuera del repo (`*_file` o variables).
- **SHOULD** silencios con caducidad y autor; revisión mensual de alertas ruidosas.
- **MUST NOT** usar `repeat_interval` muy corto como sustituto de escalado.
- La herramienta de guardia (PagerDuty u otra) es de pago: por defecto, receiver webhook/Slack/email y la herramienta como adaptador opcional (D16).

## Por qué
La fatiga de alertas hace que se ignoren las críticas. Agrupar e inhibir reduce una tormenta a una notificación con la causa. Sin watchdog, "no hay alertas" puede significar "no hay alertado".

## Ejemplos
### Mal
```yaml
- alert: HighCPU
  expr: node_cpu_utilisation > 0.8
  labels: { severity: critical }     # page por una causa, sin runbook
```
### Bien
```yaml
groups:
  - name: orders-slo
    rules:
      - alert: OrdersHighErrorBudgetBurn
        expr: job:slo_errors_per_request:ratio_rate5m{service="orders"} > (14.4 * 0.001)
        for: 2m
        labels: { severity: critical, team: payments }
        annotations:
          summary: "Orders consume error budget 14.4x"
          runbook_url: https://runbooks.example.internal/orders/error-budget
```
```yaml
route:
  receiver: default
  group_by: [cluster, alertname, namespace]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  routes:
    - matchers: [severity="critical", team="payments"]
      receiver: payments-oncall
inhibit_rules:
  - source_matchers: [severity="critical"]
    target_matchers: [severity="warning"]
    equal: [namespace, service]
```

## Checklist de revisión
- [ ] Cada alerta de página tiene `runbook_url` y es accionable.
- [ ] Agrupación, tiempos e inhibiciones explícitos.
- [ ] Alerta watchdog enrutada fuera del clúster.
- [ ] Receivers sin secretos en claro; Alertmanager en clúster.
- [ ] Rotación de guardia y escalado documentados.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| `promtool check rules` / `amtool check-config` en CI | 1 | pendiente: pipeline del proyecto generado |
| Regla Conftest: alerta `critical` sin `runbook_url` | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de ruido de alertas | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `dashboards-and-slos-as-code`, `metrics-store-ha-retention`, `status-page-and-comms`, `observability-of-the-platform-itself`.
- Fuentes oficiales: https://prometheus.io/docs/alerting/latest/configuration/ (verificado 2026-11-07: campos de route, defaults 30s/5m/4h, `inhibit_rules`). Umbral 14.4 de burn rate: método de ventanas múltiples del libro SRE de Google.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
