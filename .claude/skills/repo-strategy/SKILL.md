---
name: repo-strategy
description: "Usar al decidir la estructura de repositorios GitOps: código vs manifiestos, mono vs multi-repo, carpetas por entorno y propiedad."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Estrategia de repositorios GitOps

## Cuándo aplicar y cuándo no
- Aplica al diseñar cómo se organizan manifiestos, charts y overlays que Argo CD sincroniza (D21, ADR-0021).
- No aplica al layout del código Java/React de la aplicación ni al estado de Terraform (ver `terraform-*`).

## Reglas
- **MUST** separar el repo de código de la aplicación del repo de manifiestos de entorno (`<org>-gitops`): el CI de la app no debe poder reescribir cualquier carpeta.
- **MUST** representar cada entorno como una carpeta (`envs/dev`, `envs/staging`, `envs/prod`), no como ramas de larga vida.
- **MUST** fijar `targetRevision` a una rama protegida o a un tag/SHA; `HEAD` implícito está prohibido en `prod`.
- **MUST** proteger la rama principal del repo GitOps: PR obligatoria, revisión, checks de `kubeconform` y `conftest`.
- **SHOULD** usar Kustomize (bases + overlays) o Helm con `values-<env>.yaml`; un único mecanismo por servicio.
- **SHOULD** un repo por dominio/equipo para repos grandes; un solo repo de plataforma para addons de clúster.
- **MUST NOT** guardar `Secret` con datos en el repo (ver `secrets-in-gitops`).
- **MUST NOT** mezclar manifiestos de clústeres distintos en la misma carpeta sin ApplicationSet que los parametrice.

## Por qué
Git es el registro de auditoría (ADR-0011). Las ramas por entorno divergen y generan cherry-picks; las carpetas hacen que el diff entre entornos sea un `diff -r`. Separar repos limita el radio de daño de un token de CI y permite permisos distintos para quien promueve a prod.

## Ejemplos
### Mal
```text
repo: shop-service        # código + manifiestos
branches: dev, staging, prod   # cada entorno es una rama, merges manuales
k8s/secret.yaml           # password en claro
```
### Bien
```text
shop-gitops/
  apps/shop-service/base/{deployment,service,kustomization}.yaml
  apps/shop-service/overlays/{dev,staging,prod}/kustomization.yaml
  clusters/{dev,prod-eu,prod-dr}/applicationset.yaml
  projects/shop-project.yaml
```
```yaml
# Application apuntando a un tag inmutable en prod
spec:
  source:
    repoURL: https://git.example.internal/shop-gitops.git
    targetRevision: v2026.11.1
    path: apps/shop-service/overlays/prod
```

## Criterios de decisión y trampas
### Cómo decidir
- Repositorio de código y repositorio de manifiestos separados: ciclos de vida, permisos y auditoría distintos.
- Carpetas por entorno en lugar de ramas por entorno: las ramas divergen y las fusiones entre ellas son dolorosas.
- Un repositorio de manifiestos por equipo o por dominio cuando la escala o los permisos lo piden.
### Trampas frecuentes
- Ramas por entorno que acaban distintas.
- Manifiestos dentro del repositorio de la aplicación con permisos de escritura amplios.
- `HEAD` implícito como revisión objetivo.
- Rama principal del repositorio de estado sin protección.
- Copiar manifiestos entre entornos a mano.
### Evidencia
- La rama principal está protegida y todo cambio de un entorno es un PR revisado.

## Checklist de revisión
- [ ] Código y manifiestos en repos distintos.
- [ ] Un directorio por entorno; sin ramas por entorno.
- [ ] `prod` apunta a tag/SHA o rama protegida.
- [ ] Rama protegida con PR y checks de validación de manifiestos.
- [ ] No hay Secrets con datos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: Application fuera del AppProject `default` | 1 | `policies/opa-conftest/argocd-gitops.rego` (escrita, sin ejecutar localmente) |
| Conftest: sin Secret con datos | 1 | `policies/opa-conftest/gitops-no-plain-secrets.rego` |
| Protección de rama y revisión de PR | 4 | revisión humana (configuración del proveedor Git) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `argo-cd`, `environment-promotion`, `secrets-in-gitops`, `drift-and-self-heal-policy`.
- Fuentes: Argo CD docs (https://argo-cd.readthedocs.io/en/stable/) · ADR-0011, ADR-0021 · verificado 2026-11-07. Estrategia de repos: criterio de la fábrica, no norma oficial.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
