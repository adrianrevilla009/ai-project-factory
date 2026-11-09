---
name: argo-cd
description: "Usar al definir Applications, ApplicationSets, AppProjects, RBAC, sync waves o notificaciones de Argo CD."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Argo CD: ApplicationSets, proyectos, RBAC, waves y notificaciones

## Cuándo aplicar y cuándo no
- Aplica a todo manifiesto `Application`, `ApplicationSet`, `AppProject` y a la configuración `argocd-rbac-cm` / `argocd-notifications-cm`.
- No aplica a estrategias de despliegue de pods (ver `argo-rollouts`) ni a otros motores (ver `flux-comparison`).

## Reglas
- **MUST** asignar cada Application a un AppProject restringido; el proyecto `default` permite cualquier repo, clúster y kind.
- **MUST** limitar en el AppProject `sourceRepos`, `destinations` y `clusterResourceWhitelist` (sin `*`).
- **MUST** definir `policy.default` mínimo (sin permisos o solo lectura) y roles por grupo SSO con `p, <sujeto>, <recurso>, <acción>, <proyecto>/<app>, allow`.
- **MUST** validar el RBAC con `argocd admin settings rbac validate` y `rbac can` en CI.
- **SHOULD** generar Applications multi-clúster/entorno con ApplicationSet (generadores `list`, `cluster`, `git`) y `goTemplate: true`.
- **SHOULD** ordenar dependencias con `argocd.argoproj.io/sync-wave` (defecto 0, admite negativos): CRDs y namespaces en waves bajas, apps después. Hooks con `argocd.argoproj.io/hook` (PreSync/Sync/PostSync/SyncFail).
- **SHOULD** suscribir notificaciones por anotación `notifications.argoproj.io/subscribe.<trigger>.<servicio>`; credenciales en `argocd-notifications-secret`, nunca en el ConfigMap.
- **MUST NOT** dar a un ApplicationSet acceso a repos o proyectos más amplios que los del equipo que lo crea.

## Por qué
Un ApplicationSet es un generador de Applications: quien lo edita puede desplegar en todos los clústeres que cubra. El AppProject es la frontera de seguridad real. Entre waves Argo CD espera (`ARGOCD_SYNC_WAVE_DELAY`, 2 s por defecto según la doc) y solo avanza si los recursos están sanos.

## Ejemplos
### Mal
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: {name: shop}
spec:
  project: default
  source: {repoURL: "https://git.example.internal/shop-gitops.git", targetRevision: HEAD, path: .}
  destination: {server: "https://kubernetes.default.svc", namespace: default}
```
### Bien
```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata: {name: shop, namespace: argocd}
spec:
  sourceRepos: ["https://git.example.internal/shop-gitops.git"]
  destinations:
    - {server: "https://kubernetes.default.svc", namespace: "shop-*"}
  clusterResourceWhitelist: []
  roles:
    - name: deployer
      policies: ["p, proj:shop:deployer, applications, sync, shop/*, allow"]
---
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: {name: shop-service, namespace: argocd}
spec:
  goTemplate: true
  generators:
    - list:
        elements:
          - {env: staging, server: "https://staging.example.internal"}
          - {env: prod, server: "https://prod.example.internal"}
  template:
    metadata: {name: "shop-{{.env}}"}
    spec:
      project: shop
      source:
        repoURL: https://git.example.internal/shop-gitops.git
        targetRevision: main
        path: "apps/shop-service/overlays/{{.env}}"
      destination: {server: "{{.server}}", namespace: "shop-{{.env}}"}
```
```yaml
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "-1"   # CRD/namespace antes que la app (wave 0)
```

## Criterios de decisión y trampas
### Cómo decidir
- Un proyecto por equipo o dominio con orígenes, destinos y recursos permitidos explícitos; el proyecto por defecto, sin uso.
- Una instancia por clúster o una central: la central simplifica, pero concentra el riesgo y el acceso a todos los clústeres.
- Notificaciones y estado de salud visibles para el equipo que despliega.
### Trampas frecuentes
- Permisos con comodines en los proyectos.
- Sincronización automática con poda en producción sin pensarlo.
- Aplicaciones que apuntan a una rama móvil.
- Cuentas locales compartidas en lugar de SSO.
- Ignorar diferencias de forma generalizada y ocultar la deriva real.
### Evidencia
- El RBAC se valida en CI y los proyectos no usan comodines.

## Checklist de revisión
- [ ] Ninguna Application usa `project: default`.
- [ ] AppProject sin `*` en repos/destinos.
- [ ] RBAC con `policy.default` mínimo y validado.
- [ ] Waves solo donde hay dependencia real.
- [ ] Credenciales de notificaciones en Secret.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: proyecto `default`, `*` en sourceRepos/destinations | 1 | `policies/opa-conftest/argocd-gitops.rego` (escrita, sin ejecutar localmente) |
| `argocd admin settings rbac validate` en CI | 1 | pendiente (job de CI del proyecto generado) |
| Revisión de cambios en ApplicationSets | 3 | agente revisor / humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `repo-strategy`, `drift-and-self-heal-policy`, `environment-promotion`, `eks-multi-region-and-argo-cd-multicluster`.
- Fuentes (verificadas 2026-11-07): https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/ · .../user-guide/projects/ · .../operator-manual/rbac/ · .../operator-manual/notifications/ · .../user-guide/application-set/. Progressive Syncs de ApplicationSet: la documentación lo describe como función experimental que hay que activar de forma explícita (`--enable-progressive-syncs`); revisar la página «Feature Maturity» de la versión instalada antes de apoyarse en ella (consultado el 2026-11-08).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
