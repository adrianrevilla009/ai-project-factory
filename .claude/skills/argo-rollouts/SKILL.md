---
name: argo-rollouts
description: "Usar al diseñar despliegues canary o blue-green con Argo Rollouts, incluidos pasos de tráfico y AnalysisTemplates."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Argo Rollouts: canary y blue-green con análisis

## Cuándo aplicar y cuándo no
- Aplica a servicios con tráfico real que necesitan reducir el riesgo de un despliegue (D21).
- No aplica a jobs batch ni a servicios internos sin métricas fiables: ahí basta `RollingUpdate`.

## Reglas
- **MUST** usar un `Rollout` (no `Deployment`) para servicios con canary/blue-green; el `Deployment` y el `Rollout` del mismo workload no coexisten.
- **MUST** incluir análisis automático en todo canary: paso `analysis` y/o análisis en background; un fallo aborta el rollout.
- **MUST** basar el análisis en métricas de SLO (tasa de error, latencia p95) con `successCondition` y `failureLimit` explícitos.
- **MUST** gestionar el tráfico por `trafficRouting` (Istio, D9) cuando se necesite porcentaje exacto; sin él el peso depende del número de réplicas.
- **SHOULD** usar `AnalysisTemplate` parametrizado con `args` y reutilizable entre servicios.
- **SHOULD** tratar `NaN`/ausencia de datos como fallo o inconcluso, nunca como éxito (funciones `isNaN()`, `default()`).
- **SHOULD** usar blue-green con `prePromotionAnalysis` cuando el cambio no admite versiones mezcladas (esquemas, contratos).
- **MUST NOT** usar `pause: {}` indefinido en prod sin dueño de la promoción.
- **MUST NOT** hacer promoción manual saltando el análisis salvo emergencia registrada.

## Por qué
Un canary sin análisis es un rolling update lento. El valor está en que la decisión de promover o abortar la toma una métrica, no una persona mirando un panel. Con Istio el peso se aplica en el VirtualService y es independiente de las réplicas.

## Ejemplos
### Mal
```yaml
strategy:
  canary:
    steps:
      - setWeight: 50
      - pause: {}        # alguien promociona "cuando le parezca"
```
### Bien
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata: {name: shop-service}
spec:
  replicas: 4
  selector: {matchLabels: {app: shop-service}}
  template:
    metadata: {labels: {app: shop-service}}
    spec:
      containers:
        - {name: app, image: registry.example.internal/shop-service:1.4.0}
  strategy:
    canary:
      canaryService: shop-service-canary
      stableService: shop-service-stable
      trafficRouting:
        istio:
          virtualService: {name: shop-service-vs, routes: [primary]}
      steps:
        - setWeight: 10
        - analysis:
            templates: [{templateName: error-rate}]
        - setWeight: 50
        - pause: {duration: 10m}
---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata: {name: error-rate}
spec:
  metrics:
    - name: error-rate
      interval: 1m
      count: 5
      failureLimit: 1
      successCondition: result[0] < 0.01
      provider:
        prometheus:
          address: http://prometheus.monitoring.svc:9090
          query: sum(rate(http_server_requests_seconds_count{app="shop-service",status=~"5.."}[2m])) / sum(rate(http_server_requests_seconds_count{app="shop-service"}[2m]))
```

## Criterios de decisión y trampas
### Cómo decidir
- Canary con análisis automático para servicios con tráfico suficiente; blue/green cuando necesitas conmutación instantánea y puedes pagar el doble de capacidad.
- Porcentajes exactos requieren enrutado de tráfico (malla); sin él, el reparto depende del número de réplicas.
- Análisis basado en el SLO, comparado con la versión estable.
### Trampas frecuentes
- Canary sin análisis automático: es un despliegue lento con el mismo riesgo.
- Métricas con retraso que llegan después de la decisión.
- Pasos demasiado cortos para ver el efecto.
- Dejar el rollout a medias sin responsable.
- Mezclar `Deployment` y `Rollout` para el mismo servicio.
### Evidencia
- Un rollout abortado a propósito en preproducción demuestra que el análisis detiene el avance.

## Checklist de revisión
- [ ] Todo canary tiene análisis (paso o background).
- [ ] `successCondition` y `failureLimit` definidos; sin datos no cuenta como éxito.
- [ ] `trafficRouting` con Istio si se exige porcentaje.
- [ ] Sin `pause` indefinido en prod.
- [ ] Servicios stable/canary declarados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: Rollout canary sin análisis | 1 | `policies/opa-conftest/argocd-gitops.rego` (escrita, sin ejecutar localmente) |
| Revisión de SLO y consultas del AnalysisTemplate | 3 | agente revisor / humana |

Local: kind/k3d (ADR-0034) permite probar Rollouts; la integración con Istio y Prometheus reales de AWS no se reproduce ni se ha verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `argo-cd`, `environment-promotion`, `drift-and-self-heal-policy`, `slo-error-budget-policy`.
- Fuentes (verificadas 2026-11-07): https://argo-rollouts.readthedocs.io/en/stable/features/canary/ · .../features/analysis/. `trafficRouting.istio` y `prePromotionAnalysis` existen en la documentación estable (consultado el 2026-11-08); los campos exactos se contrastan con la versión instalada.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
