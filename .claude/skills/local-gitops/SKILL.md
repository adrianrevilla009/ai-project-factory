---
name: local-gitops
description: "Usar al probar GitOps con Argo CD en el clúster local (opcional): app-of-apps contra un repositorio git local, sin tocar entornos reales."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# GitOps local (opcional)

## Cuándo aplicar y cuándo no
- Aplica cuando el equipo quiere ensayar el flujo Argo CD (sync, drift, rollback) en kind antes de describirlo para AWS.
- No aplica al ciclo diario de desarrollo (usar `dev-loop`) ni como sustituto de la promoción entre entornos; no despliega nada en AWS (ADR-0004).

## Reglas
- **MUST** ser opt-in: `make local-gitops` separado de `make local-up`; ningún perfil lo activa por defecto.
- **MUST** que Argo CD apunte a un repositorio git accesible desde el clúster (git server local en el clúster o un `file`/bare repo montado); TODO-VERIFY la opción más simple con la versión de Argo CD usada.
- **MUST** usar el patrón app-of-apps y los mismos manifiestos Kustomize que el perfil local, para no mantener dos fuentes de verdad.
- **MUST** `syncPolicy.automated` con `prune: true` y `selfHeal: true` solo en el clúster local; documentar que en los entornos reales la política la decide la guía de promoción.
- **MUST** que el destino sea `https://kubernetes.default.svc` (el clúster kind), nunca un clúster remoto.
- **SHOULD** ejecutar `policies/opa-conftest/argocd-gitops.rego` sobre las `Application` antes de aplicarlas.
- **MUST NOT** guardar credenciales de repositorio reales; usar valores `example`/`changeme`.
- **MUST NOT** usar `kubectl apply` manual sobre recursos gestionados por Argo CD (provoca drift).
- **MUST NOT** reproducir ApplicationSets multi-clúster ni multi-región: no se representan en local.

## Por qué
Ensayar el bucle de reconciliación en local detecta errores de estructura de repo y de sync antes de escribir la guía para AWS. Mantener un camino opcional evita sumar RAM y complejidad al desarrollo diario.

## Ejemplos
### Mal
```yaml
spec:
  destination: { server: https://prod-cluster.example.internal, namespace: demo }
```
### Bien
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: demo-root, namespace: argocd }
spec:
  project: default
  source:
    repoURL: http://gitea.local.svc:3000/demo/deploy.git   # git local de ejemplo
    path: deploy/apps
    targetRevision: HEAD
  destination: { server: https://kubernetes.default.svc, namespace: argocd }
  syncPolicy:
    automated: { prune: true, selfHeal: true }
```

## Checklist de revisión
- [ ] Es opt-in y no forma parte de `local-up`.
- [ ] Destino únicamente `kubernetes.default.svc`.
- [ ] Misma base Kustomize que los perfiles locales.
- [ ] Sin credenciales reales.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Rego sobre `Application` de Argo CD | 1 | `policies/opa-conftest/argocd-gitops.rego` |
| Que el flujo sea opt-in | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `argo-cd`, `local-profiles`, `dev-loop`, `cluster-tooling`.
- Fuentes: documentación de Argo CD (app-of-apps) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
