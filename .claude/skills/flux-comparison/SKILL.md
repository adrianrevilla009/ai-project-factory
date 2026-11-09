---
name: flux-comparison
description: "Usar al comparar Flux con Argo CD o al evaluar migrar; referencia T3, la decisión vigente es Argo CD (D21)."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Flux frente a Argo CD (referencia)

## Cuándo aplicar y cuándo no
- Aplica cuando alguien propone Flux o un proyecto heredado lo usa.
- No aplica a proyectos nuevos: D21 fija Argo CD + Argo Rollouts (ADR-0021).

## Reglas
- **MUST** usar Argo CD por defecto; adoptar Flux solo con ADR que reemplace o excepcione D21.
- **SHOULD** si se hereda Flux, mantener su modelo (GitRepository, Kustomization, HelmRelease) sin mezclar controladores sobre los mismos recursos.
- **MUST NOT** ejecutar Argo CD y Flux gestionando el mismo namespace.
- **SHOULD** conservar las reglas de `repo-strategy`, `secrets-in-gitops` y `environment-promotion`: son independientes de la herramienta.

## Por qué
Ambos reconcilian desde Git. Diferencias de modelo (verificar al decidir): Flux es un conjunto de controladores y CRDs (fuentes, Kustomization, HelmRelease) sin UI propia; Argo CD ofrece UI, AppProject/RBAC y ApplicationSet integrados, y Argo Rollouts cubre canary con análisis en el mismo ecosistema. La fábrica prioriza un único ecosistema (menos componentes, ADR-0011).

| Aspecto | Argo CD (D21) | Flux |
|---|---|---|
| Unidad | Application / ApplicationSet | Kustomization / HelmRelease |
| Multi-tenant | AppProject + RBAC | namespaces + impersonación |
| Entrega progresiva | Argo Rollouts | Flagger |

## Ejemplos
### Mal
```text
Dos controladores GitOps sincronizando shop-prod: pelean por el mismo Deployment.
```
### Bien
```yaml
# Equivalente conceptual en Flux (solo referencia)
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: {name: shop-prod, namespace: flux-system}
spec:
  interval: 10m
  path: ./envs/prod
  prune: true
  sourceRef: {kind: GitRepository, name: shop-gitops}
```
Versión de API `v1`.

## Criterios de decisión y trampas
### Cómo decidir
- Argo CD por defecto (ADR-0021); Flux solo si se hereda o si hay un motivo documentado.
- Si se hereda Flux, conserva su modelo en vez de mezclar los dos: cada herramienta con su ámbito.
- Las reglas de repositorio, secretos y promoción son independientes de la herramienta.
### Trampas frecuentes
- Dos herramientas reconciliando el mismo espacio de nombres.
- Migrar por afición sin problema que resolver.
- Perder las puertas de seguridad al cambiar de herramienta.
- Duplicar guías sin un dueño.
- Sin ADR que registre la excepción.
### Evidencia
- Un ADR por la excepción y un mapa de qué herramienta gestiona qué.

## Checklist de revisión
- [ ] Existe ADR si se aparta de D21.
- [ ] Un único controlador por recurso.
- [ ] Reglas de secretos y promoción aplicadas igual.

## Enforcement
Revisión humana (decisión de arquitectura en ADR). Sin artefacto automático.

## Relacionados, fuentes y mantenimiento
- Relacionados: `argo-cd`, `argo-rollouts`, `spinnaker-comparison`, `repo-strategy`.
- Fuentes (2026-11-07): https://fluxcd.io/flux/concepts/ · ADR-0021.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T3
