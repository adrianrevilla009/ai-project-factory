---
name: environment-promotion
description: "Usar al promover una versión entre entornos (dev, staging, prod) con GitOps: PRs de promoción, gates y rollback."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Promoción entre entornos con GitOps

## Cuándo aplicar y cuándo no
- Aplica a mover una versión validada de un entorno al siguiente en el repo GitOps.
- No aplica a la construcción del artefacto (ver `pipeline-architecture`); complementa a `promotion-between-environments`.

## Reglas
- **MUST** promover el mismo artefacto inmutable (digest de imagen) de un entorno al siguiente; nunca reconstruir.
- **MUST** hacer la promoción mediante un PR al repo GitOps que cambie la carpeta del entorno destino (`envs/<env>`), no editando el clúster.
- **MUST** exigir en el PR de prod: checks verdes, evidencia del entorno anterior (tests, análisis de canary) y aprobación humana.
- **SHOULD** automatizar el PR de promoción a dev/staging (bot) y dejar prod con aprobación manual.
- **SHOULD** que prod use `Rollout` con análisis (ver `argo-rollouts`); la promoción termina cuando el rollout es Healthy, no al fusionar.
- **MUST** definir rollback como `git revert` del PR de promoción; un Rollout abortado revierte tráfico, pero Git debe reflejarlo.
- **MUST NOT** saltarse staging para llegar a prod salvo emergencia registrada.
- **MUST NOT** crear ni editar `approvals/*.json` de la fábrica: las aprobaciones de la fábrica son gates humanos propios (`gate-protocol`).

## Por qué
Promover digest garantiza que lo probado es lo desplegado. El PR da trazabilidad y reversibilidad; el rollback es otro commit, no un procedimiento ad hoc.

## Ejemplos
### Mal
```text
docker build -t shop:prod .      # reconstruye para prod
kubectl set image deploy/shop shop=shop:prod   # cambio manual, sin Git
```
### Bien
```yaml
# envs/prod/kustomization.yaml (cambiado por PR "promote shop-service to prod")
images:
  - name: registry.example.internal/shop-service
    digest: sha256:0000000000000000000000000000000000000000000000000000000000000000  # example, digest ya probado en staging
```
```text
rollback: git revert <sha-del-PR-de-promoción>   # Argo CD sincroniza el estado anterior
```

## Criterios de decisión y trampas
### Cómo decidir
- Promociona el mismo digest de un entorno al siguiente mediante un PR al repositorio de estado.
- Automatiza la promoción a entornos bajos y exige aprobación humana y evidencia para producción.
- Ventanas de despliegue y congelaciones según el riesgo del negocio.
### Trampas frecuentes
- Reconstruir la imagen para cada entorno.
- Promociones por mensaje o a mano sin rastro.
- Entornos que difieren tanto que lo probado no vale en el siguiente.
- Aprobaciones rutinarias sin leer la evidencia.
- Mezclar cambios de código y de configuración en una promoción.
### Evidencia
- Cada promoción es un PR con enlaces a las pruebas y al análisis del entorno anterior.

## Checklist de revisión
- [ ] Mismo digest en todos los entornos.
- [ ] Promoción por PR a `envs/<env>`.
- [ ] Prod con aprobación humana y evidencia de staging.
- [ ] Rollback documentado como revert.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Protección de rama + aprobadores obligatorios en prod | 4 | revisión humana (configuración del proveedor Git) |
| Conftest: tag mutable (`latest`) en overlays prod | 1 | pendiente (ampliar `policies/opa-conftest/`) |
| Revisión del PR de promoción | 3 | agente revisor |

## Relacionados, fuentes y mantenimiento
- Relacionados: `repo-strategy`, `argo-rollouts`, `promotion-between-environments`, `change-and-release-management`, `drift-and-self-heal-policy`.
- Fuentes: ADR-0021 · https://argo-cd.readthedocs.io/en/stable/ (2026-11-07). Herramientas de promoción automática (p. ej. Kargo): comprobar al fijar la versión, no adoptadas.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
