---
name: observability-of-the-platform-itself
description: "Usar al monitorizar la propia plataforma de observabilidad (Prometheus, Collector, Loki, Tempo, Grafana, Alertmanager) y evitar puntos ciegos."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Observabilidad de la propia plataforma

## Cuándo aplicar y cuándo no
- Aplica a la monitorización de los componentes de D22 y de la cadena de alertado.
- No aplica a la monitorización de las aplicaciones de negocio.

## Reglas
- **MUST** una alerta "watchdog" siempre disparando hacia un servicio externo (dead man's switch) que avise cuando deje de llegar.
- **MUST** que el sistema que vigila no sea solo vigilado por sí mismo: al menos una comprobación externa (sonda blackbox desde otro dominio de fallo) a Grafana y a la entrada de alertas.
- **MUST** alertar sobre: pérdida de scrape (`up == 0`), Collector con `refused`/`dropped` en exporters y cola llena, ingesters de Loki/Tempo con errores de escritura, WAL de Prometheus, disco del TSDB y fallos de notificación de Alertmanager.
- **MUST** exponer métricas propias del Collector (telemetría interna) y recogerlas con Prometheus.
- **MUST** SLOs propios de la plataforma (frescura de datos: retraso de ingestión de logs/trazas, disponibilidad de consulta) como cualquier servicio.
- **SHOULD** tests de extremo a extremo sintéticos: emitir un log y una traza de prueba y comprobar que aparecen en Loki/Tempo en N minutos.
- **SHOULD** probar el camino de alerta regularmente (alerta de prueba mensual a cada receiver).
- **MUST NOT** enviar los logs de Loki a Loki sin bucle de protección (no etiquetar su propio ruido con el mismo pipeline sin límite).
- **MUST NOT** dar por válido un dashboard vacío: "sin datos" debe ser un estado alertable.

## Por qué
Si falla la plataforma, nadie se entera: es el fallo silencioso más caro. El watchdog invierte la lógica (la ausencia de señal es la alerta). Un dashboard sin datos parece "todo bien".

## Ejemplos
### Mal
```yaml
# Solo alertas de aplicación; nada sobre Prometheus, Collector ni Alertmanager
```
### Bien
```yaml
groups:
  - name: observability-platform
    rules:
      - alert: Watchdog
        expr: vector(1)
        labels: { severity: none }
        annotations: { summary: "Siempre activa; si deja de llegar al monitor externo, la cadena esta rota" }
      - alert: ScrapeTargetDown
        expr: up == 0
        for: 5m
        labels: { severity: warning }
      - alert: AlertmanagerNotificationsFailing
        expr: rate(alertmanager_notifications_failed_total[5m]) > 0
        for: 10m
        labels: { severity: critical }
      - alert: CollectorExporterDropping
        expr: rate(otelcol_exporter_send_failed_spans[5m]) > 0   # TODO-VERIFY nombre exacto de la metrica
        for: 5m
        labels: { severity: warning }
```

## Checklist de revisión
- [ ] Watchdog enrutado a un monitor externo.
- [ ] Sonda externa a Grafana y Alertmanager.
- [ ] Alertas de componentes (Collector, Loki, Tempo, Prometheus).
- [ ] Prueba sintética de ingestión y de notificación.
- [ ] "Sin datos" es alertable.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| `promtool check rules` y tests de reglas (`promtool test rules`) en CI | 1 | pendiente: pipeline del proyecto generado |
| Regla Conftest: existencia de la alerta Watchdog | 1 | pendiente: `policies/opa-conftest/` |
| Simulacro de caída de la plataforma (en papel) | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `alert-routing-and-oncall`, `metrics-store-ha-retention`, `collector-pipelines`, `logs-and-traces-stores`.
- Fuentes oficiales: https://prometheus.io/docs/alerting/latest/configuration/ (verificado 2026-11-07, estructura de Alertmanager); nombres de métricas internas de Collector y Alertmanager: TODO-VERIFY.
- Preparado para AWS, no verificado en real; el monitor externo debe vivir fuera de la cuenta/clúster y no se reproduce en local.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
