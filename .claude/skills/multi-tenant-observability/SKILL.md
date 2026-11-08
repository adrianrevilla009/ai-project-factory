---
name: multi-tenant-observability
description: "Usar al aislar la telemetría por equipo o entorno en Loki, Tempo, Prometheus y Grafana (tenants, cabeceras, límites por tenant)."
metadata:
  block: "18-observability-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Observabilidad multi-tenant

## Cuándo aplicar y cuándo no
- Aplica cuando varios equipos, entornos o clientes comparten la plataforma de observabilidad.
- No aplica a un clúster de un solo equipo con un único tenant; entonces basta una etiqueta `team` y se documenta.

## Reglas
- **MUST** definir el tenant como unidad de aislamiento y de límites (ingestión, retención, consultas), mapeado a equipo o entorno, no a servicio.
- **MUST** que el tenant lo inyecte el Collector gateway (cabecera `X-Scope-OrgID` en Loki/Tempo), nunca la aplicación ni el navegador.
- **MUST** habilitar multi-tenencia explícitamente (Loki `auth_enabled: true`; Tempo `multitenancy_enabled: true`; confirmar claves: comprobar al fijar la versión) y poner un proxy de autenticación delante que fije la cabecera según la identidad (Keycloak/OIDC, D-identidad).
- **MUST** un datasource de Grafana por tenant, con la cabecera fija en el datasource y permisos de carpeta/datasource por equipo.
- **MUST** límites por tenant (`limits_config`/overrides): tasa de ingestión, streams máximos, retención.
- **MUST NOT** compartir un tenant "común" para datos de distintos niveles de confidencialidad.
- **SHOULD** mantener tenants de producción y no producción separados.
- **SHOULD** en Prometheus aislar por instancia o por label `tenant` impuesto en remote write (Prometheus no tiene tenancy nativa).

## Por qué
Sin tenant, un equipo ruidoso agota la cuota de todos y cualquier usuario de Grafana puede consultar logs ajenos. Inyectar el tenant en el borde evita que un cliente suplante a otro cambiando una cabecera.

## Ejemplos
### Mal
```yaml
# Datasource sin cabecera: lee el tenant por defecto de todos
- name: loki
  type: loki
  url: http://loki-gateway.observability
```
### Bien
```yaml
apiVersion: 1
datasources:
  - name: loki-team-payments
    type: loki
    url: http://loki-gateway.observability
    jsonData:
      httpHeaderName1: X-Scope-OrgID
    secureJsonData:
      httpHeaderValue1: payments
```
```yaml
# Collector gateway: exporter con cabecera de tenant
exporters:
  otlphttp/loki:
    endpoint: http://loki-gateway.observability/otlp
    headers: { X-Scope-OrgID: payments }
```

## Checklist de revisión
- [ ] Mapa tenant a equipo documentado.
- [ ] Cabecera de tenant inyectada solo en el gateway/proxy.
- [ ] Datasources Grafana por tenant con permisos.
- [ ] Límites por tenant definidos.
- [ ] Prod y no-prod en tenants distintos.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Regla Conftest: datasources Grafana de Loki/Tempo sin cabecera de tenant | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de aislamiento | 4 | revisión humana (seguridad) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `collector-pipelines`, `logs-and-traces-stores`, `cardinality-and-cost-governance`.
- Fuentes oficiales: Grafana Loki y Tempo, secciones de multi-tenancy (https://grafana.com/docs/loki/latest/operations/multi-tenancy/ ; no verificada la redacción (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Preparado para AWS, no verificado en real. En local suele usarse un único tenant; el aislamiento real no se reproduce.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
