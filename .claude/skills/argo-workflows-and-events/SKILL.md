---
name: argo-workflows-and-events
description: "Usar al automatizar pipelines por eventos en Kubernetes con Argo Workflows y Argo Events, y al decidir si encajan frente a GitHub Actions."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Argo Workflows y Argo Events

## Cuándo aplicar y cuándo no
- Aplica a tareas orquestadas dentro del clúster: jobs de datos, validaciones post-despliegue, DAGs de contenedores, disparos por evento.
- No aplica al CI principal (GitHub Actions, ADR-0020) ni al despliegue (Argo CD / Rollouts).

## Reglas
- **MUST** mantener el CI de build/test/escaneo en GitHub Actions; Argo Workflows solo para trabajo que debe ejecutarse en el clúster.
- **MUST** definir plantillas reutilizables como `WorkflowTemplate` y programaciones como `CronWorkflow`, versionadas en el repo GitOps.
- **MUST** ejecutar workflows con una `ServiceAccount` dedicada de mínimo privilegio por namespace.
- **MUST** fijar `activeDeadlineSeconds`, `ttlStrategy` y límites de recursos en cada workflow.
- **SHOULD** usar Argo Events (EventSource + Sensor) para disparar workflows desde webhooks, colas o calendario; autenticar el endpoint del EventSource.
- **SHOULD** que los workflows sean idempotentes (reintentos con `retryStrategy`).
- **MUST NOT** usar Workflows para desplegar a producción saltándose Argo CD (rompería la fuente de verdad en Git).
- **MUST NOT** exponer un EventSource webhook sin autenticación.

## Por qué
Dos orquestadores para lo mismo duplican operación. Workflows aporta ejecución nativa en Kubernetes (cada paso es un contenedor, DAG o secuencia); no sustituye al CI. Un trigger por evento sin autenticar es una puerta para lanzar pods arbitrarios.

## Ejemplos
### Mal
```yaml
kind: Workflow
spec:
  entrypoint: deploy
  templates:
    - name: deploy
      container: {image: bitnami/kubectl, command: [kubectl, apply, -f, prod.yaml]}   # despliegue fuera de GitOps
```
### Bien
```yaml
apiVersion: argoproj.io/v1alpha1
kind: CronWorkflow
metadata: {name: nightly-smoke}
spec:
  schedule: "0 3 * * *"
  workflowSpec:
    serviceAccountName: wf-smoke
    activeDeadlineSeconds: 900
    ttlStrategy: {secondsAfterCompletion: 3600}
    entrypoint: smoke
    templates:
      - name: smoke
        retryStrategy: {limit: 2}
        container:
          image: registry.example.internal/smoke-tests:1.0.0
          resources: {limits: {cpu: 500m, memory: 256Mi}}
```

## Criterios de decisión y trampas
### Cómo decidir
- Argo Workflows para trabajos de larga duración o con grafo de dependencias en el clúster; el CI normal sigue en el motor de CI.
- Plantillas reutilizables y cuentas de servicio de mínimo privilegio por espacio de nombres.
### Trampas frecuentes
- Convertirlo en un segundo sistema de CI.
- Workflows sin límites de tiempo ni de recursos.
- Eventos disparados por fuentes no autenticadas.
- Sin limpieza de ejecuciones antiguas.
- Una cuenta de servicio con permisos de administrador del clúster.
### Evidencia
- Cada workflow declara tiempo máximo, recursos y retención.

## Checklist de revisión
- [ ] Es trabajo in-cluster que no cabe en GitHub Actions.
- [ ] ServiceAccount propia, deadline, TTL y límites.
- [ ] Plantillas en `WorkflowTemplate`.
- [ ] EventSource autenticado.
- [ ] No despliega fuera de Argo CD.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de workflows y EventSources | 3 | agente revisor / humana |
| Política Kyverno para exigir deadline/límites | 1 | pendiente (`policies/kyverno/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `argo-cd`, `argo-rollouts`, `environment-promotion`, `container-and-k8s-security`.
- Fuentes (2026-11-07): https://argo-workflows.readthedocs.io/en/stable/ (describe el motor como CRD que orquesta jobs paralelos en Kubernetes). Detalles de CRDs y de Argo Events (Sensor/EventSource).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
