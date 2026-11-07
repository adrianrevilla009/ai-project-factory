---
name: dashboards-and-slos-as-code
description: "Usar al crear dashboards de Grafana y SLOs: versionados como código, provisionados y con reglas de burn rate generadas."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Dashboards y SLOs como código

## Cuándo aplicar y cuándo no
- Aplica a todo dashboard, SLO y regla de grabación/alerta derivada que viva en la plataforma D22.
- No aplica a exploración ad hoc en Grafana (Explore), que no se persiste.

## Reglas
- **MUST** versionar dashboards en Git (JSON exportado o generado con Grafonnet/Jsonnet u otra librería) y provisionarlos por fichero (`providers` de dashboards) o por ConfigMap; la edición en la UI no es fuente de verdad.
- **MUST** `allowUiUpdates: false` en el provider de producción para que la UI no diverja de Git.
- **MUST** definir cada SLO en una spec declarativa (objetivo, ventana, SLI en PromQL) de la que se generan reglas de grabación y alertas de burn rate multiventana; no escribir esas reglas a mano.
- **MUST** `uid` estable y `title` único por dashboard; datasources por `uid`, no por nombre.
- **MUST** que todo dashboard de servicio use variables (`namespace`, `service`) y muestre los 4 golden signals (latencia, tráfico, errores, saturación) más el SLO.
- **SHOULD** el SLO vive en el repo del servicio; los dashboards de plataforma, en el repo de plataforma.
- **SHOULD** el generador de SLOs sea de código abierto (p. ej. Sloth o Pyrra; elegir por ADR, TODO-VERIFY formato de spec vigente).
- **MUST NOT** SLOs al 100% ni sin ventana; el objetivo debe tener error budget con política asociada.

## Por qué
Dashboards editados en la UI se pierden, divergen entre entornos y no se revisan. Las reglas de burn rate multiventana son fáciles de errar a mano; generarlas de una spec garantiza consistencia y permite revisar solo el objetivo.

## Ejemplos
### Mal
```text
Dashboard creado en la UI de produccion, sin uid fijo, con datasource "prometheus-1" por nombre.
Alertas de SLO copiadas a mano con umbrales distintos por servicio.
```
### Bien
```yaml
# /etc/grafana/provisioning/dashboards/platform.yaml
apiVersion: 1
providers:
  - name: services
    folder: Services
    type: file
    allowUiUpdates: false
    options: { path: /var/lib/grafana/dashboards }
```
```yaml
# slo/orders.yaml (spec Sloth, TODO-VERIFY version del esquema)
version: "prometheus/v1"
service: "orders"
slos:
  - name: "requests-availability"
    objective: 99.9
    sli:
      events:
        error_query: sum(rate(http_server_requests_seconds_count{service="orders",status=~"5.."}[{{.window}}]))
        total_query: sum(rate(http_server_requests_seconds_count{service="orders"}[{{.window}}]))
    alerting:
      name: OrdersAvailability
      page_alert:   { labels: { severity: critical } }
      ticket_alert: { labels: { severity: warning } }
```

## Checklist de revisión
- [ ] Dashboards y SLOs en Git; provisioning sin edición por UI.
- [ ] `uid` estable y datasource por uid.
- [ ] SLO con objetivo, ventana y política de error budget.
- [ ] Reglas generadas, no escritas a mano; pasan `promtool check rules`.
- [ ] Variables y golden signals presentes.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Validación de JSON de dashboards (uid, datasource por uid) con Conftest | 1 | pendiente: `policies/opa-conftest/` |
| Generación y `promtool check rules` en CI | 1 | pendiente: pipeline del proyecto generado |
| Revisión del objetivo del SLO | 4 | revisión humana (dueño del servicio) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `alert-routing-and-oncall`, `tempo-and-service-graphs`, `cardinality-and-cost-governance`, `slo-error-budget-policy` (bloque 19).
- Fuentes oficiales: Grafana, provisioning de dashboards (https://grafana.com/docs/grafana/latest/administration/provisioning/ ; no verificada en esta sesión, TODO-VERIFY). Herramientas SLO: documentación de Sloth/Pyrra, TODO-VERIFY.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
