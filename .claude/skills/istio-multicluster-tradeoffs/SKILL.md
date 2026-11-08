---
name: istio-multicluster-tradeoffs
description: "Usar al decidir si extender Istio a varios clústeres/regiones: multi-primary vs primary-remote, redes, failover por localidad y coste operativo."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Istio multicluster: trade-offs

## Cuándo aplicar y cuándo no
- Aplica al evaluar una malla Istio que abarque clústeres EKS de varias AZ/regiones o un híbrido on-prem.
- No aplica si cada región puede ser una malla aislada con failover en DNS/borde (suele ser más simple y de menor radio de impacto).
- Diseño en papel; preparado para AWS, no verificado en real. Local (kind/k3d) NO reproduce redes multi-región ni latencia entre regiones.

## Reglas
- **MUST** justificar por escrito por qué hace falta una malla compartida; la opción por defecto es una malla por región.
- **MUST** elegir el modelo de plano de control: multi-primary (un control plane por clúster, fallo acotado, configuración a sincronizar) o primary-remote (más simple, dependencia centralizada).
- **MUST** declarar la topología de red: red única (IPs sin solapamiento, conectividad directa) o multi-red (gateways este-oeste, permite rangos solapados).
- **MUST** asegurar que la misma configuración (`VirtualService`, `AuthorizationPolicy`) se aplica a todos los clústeres vía GitOps (`eks-multi-region-and-argo-cd-multicluster`); la deriva rompe el failover.
- **MUST** definir identidad y raíz de confianza compartida (CA común o intermedia por clúster) y su rotación.
- **MUST NOT** depender del control plane de un único clúster para que el tráfico de la región superviviente siga funcionando (`static-stability-and-cell-architecture`).
- **SHOULD** usar balanceo por localidad con `outlierDetection` para failover automático; medir el tráfico entre regiones (coste de transferencia, `finops-of-resilience`).
- **SHOULD** limitar el alcance de endpoints visibles entre clústeres a los servicios que lo necesitan.
- **SHOULD** valorar el modo ambient/sidecar según la versión adoptada (ambient es GA desde Istio 1.24; su multicluster multi-red es beta desde 1.29 y el multicluster alfa se introdujo en 1.27; comprobar en la página «Feature Status» de la versión adoptada).

## Por qué
La documentación de Istio describe multi-primary como más disponible (un control plane caído limita el alcance de la caída) a cambio de coordinar la configuración, y primary-remote como más simple con dependencia centralizada. Cada clúster añadido amplía el dominio de fallo de una configuración errónea: el fallo correlacionado es el riesgo real.

## Ejemplos
### Mal
```yaml
# Failover global sin detección de outliers ni límites: tráfico cruzado a ciegas
trafficPolicy:
  loadBalancer: {simple: ROUND_ROBIN}
```
### Bien
```yaml
apiVersion: networking.istio.io/v1
kind: DestinationRule
metadata: {name: orders}
spec:
  host: orders.shop.svc.cluster.local
  trafficPolicy:
    loadBalancer:
      localityLbSetting: {enabled: true}
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 10s
      baseEjectionTime: 30s
```
`outlierDetection` es necesario para que el failover por localidad se active (comprobar en docs de la versión adoptada).

## Checklist de revisión
- [ ] Justificada la malla compartida frente a mallas por región.
- [ ] Modelo de control plane y de red documentados.
- [ ] CA y rotación definidas.
- [ ] Coste de tráfico entre regiones estimado.
- [ ] Prueba de pérdida de un control plane en papel (`fault-injection-and-game-days`).

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Kyverno: exigir `outlierDetection` en `DestinationRule` | 1 | pendiente: `policies/kyverno/` |
| Revisión humana del ADR de topología | 4 | PR / gate |

## Relacionados, fuentes y mantenimiento
- Relacionados: `multi-region-patterns`, `static-stability-and-cell-architecture`, `eks-multi-region-and-argo-cd-multicluster`, `dependency-mapping-and-blast-radius`.
- Fuentes (verificado 2026-11-07): https://istio.io/latest/docs/ops/deployment/deployment-models/ . Estado de ambient (GA en 1.24) y de su multicluster (beta en 1.29): istio.io/latest/docs/releases/feature-stages/ y el blog de Istio de 2025-2026.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
