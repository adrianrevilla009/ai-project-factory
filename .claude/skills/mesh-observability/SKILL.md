---
name: mesh-observability
description: "Usar al configurar métricas, trazas y visualización de la malla Istio con Prometheus, tracing y Kiali."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Observabilidad de la malla (Kiali)

## Cuándo aplicar y cuándo no
- Aplica a clústeres con Istio donde se necesita ver topología, tasas de error y latencia entre servicios.
- No sustituye la observabilidad de aplicación (logs estructurados, métricas de negocio, trazas con contexto): la complementa.

## Reglas
- **MUST** recoger las métricas estándar de Istio (p. ej. `istio_requests_total`, `istio_request_duration_milliseconds`) en Prometheus; nombres verificados en la referencia de métricas de istio.io el 2026-11-08.
- **MUST** instalar Kiali (OSS) solo como herramienta interna; acceso autenticado y fuera del gateway público.
- **MUST** propagar cabeceras de trazado (W3C `traceparent`/B3) desde la aplicación: la malla no puede unir spans si la app no las reenvía.
- **SHOULD** configurar muestreo de trazas bajo por defecto (p. ej. 1 %) y subirlo temporalmente al depurar.
- **SHOULD** definir alertas sobre la tasa de 5xx y la latencia p99 por servicio, ligadas a SLO.
- **MUST NOT** registrar cuerpos de petición ni datos personales en los access logs de Envoy.
- **MUST NOT** dejar el dashboard de Kiali con la configuración de demo en entornos compartidos.

## Por qué
La malla da observabilidad uniforme "gratis" por servicio, pero sin propagación de contexto en la aplicación las trazas quedan rotas. Los access logs de Envoy pueden filtrar datos sensibles si se amplían sin criterio.

## Ejemplos
### Mal
```yaml
# Telemetría con muestreo del 100 % y logs de todo en producción
apiVersion: telemetry.istio.io/v1
kind: Telemetry
metadata: { name: all, namespace: istio-system }
spec:
  tracing:
    - randomSamplingPercentage: 100.0
```
### Bien
```yaml
apiVersion: telemetry.istio.io/v1
kind: Telemetry
metadata: { name: default, namespace: istio-system }
spec:
  tracing:
    - randomSamplingPercentage: 1.0
  accessLogging:
    - providers: [{ name: envoy }]
      filter:
        expression: "response.code >= 400"
```
`telemetry.istio.io/v1` se sirve en el CRD de Istio (verificado el 2026-11-08); los proveedores concretos dependen de la configuración de la malla.

## Checklist de revisión
- [ ] Prometheus recoge métricas de Envoy/Istio.
- [ ] Kiali no está expuesto públicamente.
- [ ] La app reenvía cabeceras de trazado.
- [ ] Muestreo y access logs acotados.
- [ ] Alertas de 5xx/latencia definidas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de `Telemetry` y exposición de Kiali | 3 | agente `code-reviewer` |
| Regla Conftest para Kiali público (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `logging-rules`, `traffic-management`, `canary-and-traffic-splitting`, `ingress-and-egress-gateways`.
- Fuentes: istio.io/latest/docs/tasks/observability/ y kiali.io/docs (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
