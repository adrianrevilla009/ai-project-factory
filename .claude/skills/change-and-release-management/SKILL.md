---
name: change-and-release-management
description: "Usar al diseñar el proceso de cambios y despliegues seguros: canary por celda/región, ventanas, rollback, congelaciones y vínculo con el presupuesto de error."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Gestión de cambios y releases

## Cuándo aplicar y cuándo no
- Aplica a despliegues de aplicación, cambios de IaC, migraciones y cambios de configuración en servicios con tier.
- No aplica a la mecánica de pipelines (ver bloque CI/CD); aquí se define el control de riesgo.

## Reglas
- **MUST** clasificar el cambio por riesgo (estándar, normal, de emergencia) según tier y radio de impacto (`dependency-mapping-and-blast-radius`).
- **MUST** desplegar de forma progresiva: una celda o región canaria, observación contra SLO y avance por oleadas; nunca todas las regiones a la vez.
- **MUST** tener rollback probado y un plan de reversión para cada cambio; si la migración de datos es irreversible, exigir patrón expand/contract (`schema-migrations`).
- **MUST** automatizar el freno: la promoción se detiene si empeoran los SLIs del canary.
- **MUST** respetar la congelación de cambios activada por el agotamiento del presupuesto de error (`slo-error-budget-policy`), salvo P0 y correcciones de seguridad.
- **MUST** tratar la configuración y los feature flags como cambios con el mismo control que el código.
- **SHOULD** evitar cambios en horas de baja cobertura de guardia y antes de periodos de pico.
- **SHOULD** registrar cada cambio (qué, quién aprueba, cuándo, enlace al commit) para correlacionar con incidentes.
- **MUST NOT** aplicar cambios manuales en consola; todo por IaC/GitOps. La fábrica nunca aplica cambios a AWS (ADR-0004).

## Por qué
La mayoría de incidentes empiezan con un cambio. Reducir el radio de impacto con oleadas y celdas (`static-stability-and-cell-architecture`) convierte un fallo regional en uno de una celda. Vincular el proceso al presupuesto de error alinea velocidad y fiabilidad sin discusiones.

## Ejemplos
### Mal
```text
Despliegue viernes 17:30 a todas las regiones a la vez, sin rollback ensayado.
```
### Bien
```yaml
# release-policy.yaml (diseño; preparado para AWS, no verificado en real)
service: orders-api
risk: normal
waves:
  - {name: canary-cell, region: eu-west-1, traffic: 5%, bake: 30m}
  - {name: region-1, region: eu-west-1, traffic: 100%, bake: 60m}
  - {name: region-2, region: eu-central-1, traffic: 100%, bake: 60m}
abort_if:
  - "slo.availability.burn_rate_1h > 6"
  - "p95_latency_ms > 300 for 10m"
rollback: "argo rollouts undo / git revert; probado en game day"
blocked_when: "error_budget.remaining <= 0 unless label=P0|security"
```

## Checklist de revisión
- [ ] Riesgo clasificado y aprobación proporcional.
- [ ] Oleadas con canary y criterios de aborto.
- [ ] Rollback probado; migraciones expand/contract.
- [ ] Congelación por presupuesto de error respetada.
- [ ] Registro del cambio enlazado a commits.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest sobre `release-policy.yaml` (waves y abort_if obligatorios) | 1 | pendiente: `policies/opa-conftest/` |
| Gate que consulta el presupuesto de error antes de promover | 2 | pendiente |
| Revisión humana de cambios de riesgo alto | 4 | PR / CAB ligero |

## Relacionados, fuentes y mantenimiento
- Relacionados: `slo-error-budget-policy`, `eks-multi-region-and-argo-cd-multicluster`, `incident-management-and-postmortems`, `schema-migrations`, `dependency-mapping-and-blast-radius`.
- Fuentes: Well-Architected Operational Excellence / Reliability (cambios); Argo Rollouts.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
