# Estándares · 17-gitops-progressive-delivery

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## argo-cd

- **MUST** asignar cada Application a un AppProject restringido; el proyecto `default` permite cualquier repo, clúster y kind.
- **MUST** limitar en el AppProject `sourceRepos`, `destinations` y `clusterResourceWhitelist` (sin `*`).
- **MUST** definir `policy.default` mínimo (sin permisos o solo lectura) y roles por grupo SSO con `p, <sujeto>, <recurso>, <acción>, <proyecto>/<app>, allow`.
- **MUST** validar el RBAC con `argocd admin settings rbac validate` y `rbac can` en CI.
- **SHOULD** generar Applications multi-clúster/entorno con ApplicationSet (generadores `list`, `cluster`, `git`) y `goTemplate: true`.
- **SHOULD** ordenar dependencias con `argocd.argoproj.io/sync-wave` (defecto 0, admite negativos): CRDs y namespaces en waves bajas, apps después. Hooks con `argocd.argoproj.io/hook` (PreSync/Sync/PostSync/SyncFail).
- **SHOULD** suscribir notificaciones por anotación `notifications.argoproj.io/subscribe.<trigger>.<servicio>`; credenciales en `argocd-notifications-secret`, nunca en el ConfigMap.
- **MUST NOT** dar a un ApplicationSet acceso a repos o proyectos más amplios que los del equipo que lo crea.

## argo-rollouts

- **MUST** usar un `Rollout` (no `Deployment`) para servicios con canary/blue-green; el `Deployment` y el `Rollout` del mismo workload no coexisten.
- **MUST** incluir análisis automático en todo canary: paso `analysis` y/o análisis en background; un fallo aborta el rollout.
- **MUST** basar el análisis en métricas de SLO (tasa de error, latencia p95) con `successCondition` y `failureLimit` explícitos.
- **MUST** gestionar el tráfico por `trafficRouting` (Istio, D9) cuando se necesite porcentaje exacto; sin él el peso depende del número de réplicas.
- **SHOULD** usar `AnalysisTemplate` parametrizado con `args` y reutilizable entre servicios.
- **SHOULD** tratar `NaN`/ausencia de datos como fallo o inconcluso, nunca como éxito (funciones `isNaN()`, `default()`).
- **SHOULD** usar blue-green con `prePromotionAnalysis` cuando el cambio no admite versiones mezcladas (esquemas, contratos).
- **MUST NOT** usar `pause: {}` indefinido en prod sin dueño de la promoción.
- **MUST NOT** hacer promoción manual saltando el análisis salvo emergencia registrada.

## argo-workflows-and-events

- **MUST** mantener el CI de build/test/escaneo en GitHub Actions; Argo Workflows solo para trabajo que debe ejecutarse en el clúster.
- **MUST** definir plantillas reutilizables como `WorkflowTemplate` y programaciones como `CronWorkflow`, versionadas en el repo GitOps.
- **MUST** ejecutar workflows con una `ServiceAccount` dedicada de mínimo privilegio por namespace.
- **MUST** fijar `activeDeadlineSeconds`, `ttlStrategy` y límites de recursos en cada workflow.
- **SHOULD** usar Argo Events (EventSource + Sensor) para disparar workflows desde webhooks, colas o calendario; autenticar el endpoint del EventSource.
- **SHOULD** que los workflows sean idempotentes (reintentos con `retryStrategy`).
- **MUST NOT** usar Workflows para desplegar a producción saltándose Argo CD (rompería la fuente de verdad en Git).
- **MUST NOT** exponer un EventSource webhook sin autenticación.

## drift-and-self-heal-policy

- **MUST** definir explícitamente por entorno `syncPolicy.automated` con `prune` y `selfHeal`; los defectos de Argo CD son `prune: false` y `selfHeal: false`.
- **SHOULD** `dev`/`staging`: `automated` + `prune: true` + `selfHeal: true`. `prod`: sync automático de lo ya promovido en Git, `selfHeal: true`, `prune` solo tras revisión (o sync manual con ventana).
- **MUST** tratar el cambio manual en el clúster como incidente de proceso: corregir en Git, no con `kubectl edit`.
- **MUST** acotar `ignoreDifferences` a campos concretos (`jsonPointers`/`jqPathExpressions`) de kinds concretos, con comentario del motivo (p. ej. `/spec/replicas` gestionado por HPA).
- **SHOULD** usar `syncOptions: [RespectIgnoreDifferences=true]` cuando el campo ignorado no deba reescribirse al sincronizar (TODO-VERIFY).
- **SHOULD** usar `syncWindows` del AppProject para limitar cuándo prod se sincroniza.
- **MUST NOT** usar `ignoreDifferences` global para silenciar diffs que no se entienden.
- **MUST NOT** activar `allowEmpty: true` salvo caso justificado (evita vaciar una app por error).

## environment-promotion

- **MUST** promover el mismo artefacto inmutable (digest de imagen) de un entorno al siguiente; nunca reconstruir.
- **MUST** hacer la promoción mediante un PR al repo GitOps que cambie la carpeta del entorno destino (`envs/<env>`), no editando el clúster.
- **MUST** exigir en el PR de prod: checks verdes, evidencia del entorno anterior (tests, análisis de canary) y aprobación humana.
- **SHOULD** automatizar el PR de promoción a dev/staging (bot) y dejar prod con aprobación manual.
- **SHOULD** que prod use `Rollout` con análisis (ver `argo-rollouts`); la promoción termina cuando el rollout es Healthy, no al fusionar.
- **MUST** definir rollback como `git revert` del PR de promoción; un Rollout abortado revierte tráfico, pero Git debe reflejarlo.
- **MUST NOT** saltarse staging para llegar a prod salvo emergencia registrada.
- **MUST NOT** crear ni editar `approvals/*.json` de la fábrica: las aprobaciones de la fábrica son gates humanos propios (`gate-protocol`).

## flux-comparison

- **MUST** usar Argo CD por defecto; adoptar Flux solo con ADR que reemplace o excepcione D21.
- **SHOULD** si se hereda Flux, mantener su modelo (GitRepository, Kustomization, HelmRelease) sin mezclar controladores sobre los mismos recursos.
- **MUST NOT** ejecutar Argo CD y Flux gestionando el mismo namespace.
- **SHOULD** conservar las reglas de `repo-strategy`, `secrets-in-gitops` y `environment-promotion`: son independientes de la herramienta.

## repo-strategy

- **MUST** separar el repo de código de la aplicación del repo de manifiestos de entorno (`<org>-gitops`): el CI de la app no debe poder reescribir cualquier carpeta.
- **MUST** representar cada entorno como una carpeta (`envs/dev`, `envs/staging`, `envs/prod`), no como ramas de larga vida.
- **MUST** fijar `targetRevision` a una rama protegida o a un tag/SHA; `HEAD` implícito está prohibido en `prod`.
- **MUST** proteger la rama principal del repo GitOps: PR obligatoria, revisión, checks de `kubeconform` y `conftest`.
- **SHOULD** usar Kustomize (bases + overlays) o Helm con `values-<env>.yaml`; un único mecanismo por servicio.
- **SHOULD** un repo por dominio/equipo para repos grandes; un solo repo de plataforma para addons de clúster.
- **MUST NOT** guardar `Secret` con datos en el repo (ver `secrets-in-gitops`).
- **MUST NOT** mezclar manifiestos de clústeres distintos en la misma carpeta sin ApplicationSet que los parametrice.

## secrets-in-gitops

- **MUST NOT** commitear `Secret` con `data`/`stringData` reales en el repo GitOps.
- **MUST** gestionar los secretos en el clúster destino con un operador: External Secrets Operator o Vault Secrets Operator contra Vault OSS (ADR-0010/0031); Sealed Secrets como alternativa sin backend. El repo solo contiene la referencia (`ExternalSecret`).
- **MUST NOT** inyectar secretos en la generación de manifiestos (plugins tipo argocd-vault-plugin): Argo CD guarda manifiestos generados en la caché Redis en claro.
- **SHOULD** que la actualización del secreto esté desacoplada del sync de la aplicación.
- **SHOULD** rotar con TTL corto/credenciales dinámicas (ver `dynamic-database-credentials`).
- **MUST** pasar un escáner de secretos (gitleaks o similar) en el pre-commit y en CI del repo GitOps.
- **MUST NOT** usar licencias de pago por defecto (D16): Vault OSS/OpenBao, no Vault Enterprise.

## spinnaker-comparison

- **MUST** usar Argo CD + Rollouts por defecto; Spinnaker solo con ADR que excepcione D21.
- **MUST NOT** introducir Spinnaker solo para canary: Argo Rollouts con `AnalysisTemplate` cubre el caso con menos componentes.
- **SHOULD** si se hereda, aislar su ámbito (aplicaciones y cuentas concretas) y migrar a manifiestos declarativos en Git de forma incremental (strangler, ver `strangler-fig-migration`).
- **SHOULD** mantener las reglas de promoción y secretos agnósticas a la herramienta.
