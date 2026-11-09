---
name: drift-and-self-heal-policy
description: "Usar al decidir prune, selfHeal, ignoreDifferences y política de cambios manuales (drift) en Applications de Argo CD por entorno."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Política de deriva (drift) y self-heal

## Cuándo aplicar y cuándo no
- Aplica a `spec.syncPolicy` e `ignoreDifferences` de cada Application/ApplicationSet.
- No aplica a la deriva de infraestructura Terraform (ver `terraform-*`).

## Reglas
- **MUST** definir explícitamente por entorno `syncPolicy.automated` con `prune` y `selfHeal`; los defectos de Argo CD son `prune: false` y `selfHeal: false`.
- **SHOULD** `dev`/`staging`: `automated` + `prune: true` + `selfHeal: true`. `prod`: sync automático de lo ya promovido en Git, `selfHeal: true`, `prune` solo tras revisión (o sync manual con ventana).
- **MUST** tratar el cambio manual en el clúster como incidente de proceso: corregir en Git, no con `kubectl edit`.
- **MUST** acotar `ignoreDifferences` a campos concretos (`jsonPointers`/`jqPathExpressions`) de kinds concretos, con comentario del motivo (p. ej. `/spec/replicas` gestionado por HPA).
- **SHOULD** usar `syncOptions: [RespectIgnoreDifferences=true]` cuando el campo ignorado no deba reescribirse al sincronizar.
- **SHOULD** usar `syncWindows` del AppProject para limitar cuándo prod se sincroniza.
- **MUST NOT** usar `ignoreDifferences` global para silenciar diffs que no se entienden.
- **MUST NOT** activar `allowEmpty: true` salvo caso justificado (evita vaciar una app por error).

## Por qué
Sin self-heal, Git deja de ser la verdad y el siguiente sync puede sorprender. Con prune descontrolado, un path mal escrito borra recursos. Los webhooks mutadores y HPA generan diffs legítimos: se declaran, no se ignoran en bloque.

## Ejemplos
### Mal
```yaml
syncPolicy:
  automated: {prune: true, allowEmpty: true}
ignoreDifferences:
  - group: "*"
    kind: "*"
    jsonPointers: ["/spec"]
```
### Bien
```yaml
syncPolicy:
  automated:
    prune: false        # prod: prune tras revisión
    selfHeal: true
  syncOptions:
    - RespectIgnoreDifferences=true
ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers: ["/spec/replicas"]   # gestionado por HPA
```

## Criterios de decisión y trampas
### Cómo decidir
- En desarrollo y staging, autocorrección y poda; en producción, sincronización automática de lo seguro y aprobación humana para lo destructivo.
- El cambio manual es un incidente de proceso: se corrige en Git, no con `kubectl`.
- Ignora diferencias solo en campos concretos que un controlador gestiona legítimamente (por ejemplo, réplicas con HPA).
### Trampas frecuentes
- Activar poda en producción sin una red de seguridad.
- Ignorar diferencias en recursos enteros.
- Que la autocorrección pelee con otro controlador en bucle.
- Cambios de emergencia manuales que nunca se llevan a Git.
- Alertas de deriva sin responsable.
### Evidencia
- Un informe de aplicaciones desincronizadas y de cambios manuales detectados, revisado de forma periódica.

## Checklist de revisión
- [ ] `prune`/`selfHeal` explícitos y coherentes con el entorno.
- [ ] Cada `ignoreDifferences` es específico y comentado.
- [ ] Sin `allowEmpty` injustificado.
- [ ] Hay procedimiento para cambios de emergencia vía PR.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: `ignoreDifferences` con `*` / `allowEmpty` en prod | 1 | pendiente (ampliar `policies/opa-conftest/argocd-gitops.rego`) |
| Alerta de apps OutOfSync prolongado | 2 | pendiente (bloque 18) |
| Revisión de syncPolicy en PR | 3 | agente revisor / humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `argo-cd`, `environment-promotion`, `repo-strategy`.
- Fuentes (verificadas 2026-11-07): https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/ (defectos prune/selfHeal/allowEmpty desactivados; reconciliación 120 s) · .../user-guide/diffing/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
