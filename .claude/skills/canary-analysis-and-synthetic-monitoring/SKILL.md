---
name: canary-analysis-and-synthetic-monitoring
description: "Usar al definir el análisis automático de un canary (métricas, umbrales, rollback) y las comprobaciones sintéticas que vigilan flujos críticos tras un despliegue."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Análisis de canary y monitorización sintética

## Cuándo aplicar y cuándo no
- Aplica a releases progresivos (canary, ver `canary-and-traffic-splitting`) y a servicios con flujos críticos que deben vigilarse continuamente.
- No aplica a la ejecución real del despliegue: la fábrica no despliega (ADR-0004). Aquí se definen criterios y artefactos "preparados para AWS, no verificado en real".

## Reglas
- **MUST** definir antes del release las métricas de decisión (tasa de errores, latencia p95/p99, saturación, métrica de negocio) y los umbrales de promoción y de rollback, derivados del SLO.
- **MUST** comparar el canary contra la línea base estable (misma ventana, mismo tráfico) y no contra valores absolutos aislados.
- **MUST** exigir un volumen mínimo de tráfico y duración mínima antes de decidir; con poco tráfico, apoyarse en sintéticos.
- **MUST** que el rollback sea automático o de un paso, y probado.
- **MUST** tener sondas sintéticas de los flujos críticos (login, lectura clave, escritura de bajo riesgo) que usen datos de prueba etiquetados y sin efectos de negocio reales.
- **MUST NOT** usar credenciales o datos reales de clientes en sintéticos; credenciales desde el gestor de secretos.
- **MUST NOT** alertar por causa (CPU) lo que se puede alertar por síntoma (ver `alerting-symptom-based`).
- **SHOULD** diferenciar tráfico sintético en métricas y trazas con una cabecera o atributo dedicado.
- **SHOULD** incluir en el análisis el error budget restante: sin presupuesto, no se promueve (ver `slo-sli-error-budgets`).

## Por qué
Un canary sin criterios objetivos se promueve por intuición. Los sintéticos detectan caídas de flujos poco frecuentes antes que los usuarios y dan señal cuando el tráfico real es escaso.

## Ejemplos
### Mal
```text
Desplegamos al 10 %, miramos el dashboard un rato y si no se ve nada raro, al 100 %.
```
### Bien
```yaml
# Criterios de análisis (formato ilustrativo; adaptar a Argo Rollouts/Flagger, comprobar CRD y campos)
canary:
  steps: [5, 25, 50, 100]
  minDurationPerStepMinutes: 15
  minRequestsPerStep: 500
  metrics:
    - name: error-rate
      query: "sum(rate(http_server_requests_seconds_count{status=~'5..',version='canary'}[5m])) / sum(rate(http_server_requests_seconds_count{version='canary'}[5m]))"
      maxRelativeToBaseline: 1.1
      maxAbsolute: 0.01
    - name: latency-p95-ms
      maxRelativeToBaseline: 1.2
  onFailure: rollback
synthetic:
  - name: login-and-read-orders
    intervalSeconds: 60
    header: "X-Synthetic: true"
    credentialsFrom: secret/synthetic-probe   # nunca en el repositorio
```

## Criterios de decisión y trampas
### Cómo decidir
- Canary con análisis automático cuando hay tráfico suficiente; sondas sintéticas cuando no.
- Compara siempre contra la línea base estable con la misma ventana, no contra valores absolutos.
- Porcentaje y duración según el riesgo del cambio.
### Trampas frecuentes
- Decidir con poco tráfico: es ruido.
- Métricas que tardan en reflejar el problema.
- Un rollback que nunca se ha ejercitado.
- Sondas sintéticas con cuentas reales y permisos amplios.
- Olvidar una métrica de negocio, no solo técnica.
### Evidencia
- El rollback automático se ha ejercitado en preproducción.

## Checklist de revisión
- [ ] Métricas y umbrales definidos antes del release, relativos a la línea base.
- [ ] Tráfico y duración mínimos por paso.
- [ ] Rollback de un paso y probado.
- [ ] Sintéticos con datos de prueba y credenciales gestionadas.
- [ ] Tráfico sintético distinguible en observabilidad.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de los criterios de canary y sondas | 3 | agente `performance` (`.claude/agents/quality/performance.md`) |
| Regla OPA/Conftest: Rollout con análisis obligatorio | 1 | pendiente (`policies/opa-conftest/`) |
| Gate humano de release | 4 | `gates/` (revisión humana) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `canary-and-traffic-splitting`, `slo-sli-error-budgets`, `alerting-symptom-based`, `performance-testing`, `golden-signals-red-use`.
- Fuentes: Argo Rollouts (https://argo-rollouts.readthedocs.io/) y Flagger (https://docs.flagger.app/); comprobar campos y versiones a 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
