---
name: spinnaker-comparison
description: "Usar al comparar Spinnaker con Argo CD/Rollouts o al heredar pipelines de Spinnaker; referencia T3 (D21 fija Argo)."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Spinnaker frente a Argo CD + Rollouts (referencia)

## Cuándo aplicar y cuándo no
- Aplica al evaluar Spinnaker o al integrarse con una organización que lo usa.
- No aplica a proyectos nuevos: D21 fija Argo CD + Argo Rollouts (ADR-0021).

## Reglas
- **MUST** usar Argo CD + Rollouts por defecto; Spinnaker solo con ADR que excepcione D21.
- **MUST NOT** introducir Spinnaker solo para canary: Argo Rollouts con `AnalysisTemplate` cubre el caso con menos componentes.
- **SHOULD** si se hereda, aislar su ámbito (aplicaciones y cuentas concretas) y migrar a manifiestos declarativos en Git de forma incremental (strangler, ver `strangler-fig-migration`).
- **SHOULD** mantener las reglas de promoción y secretos agnósticas a la herramienta.

## Por qué
Spinnaker es una plataforma de entrega orientada a pipelines (Application, Cluster, Server Group, Pipeline, Stage) con estrategias blue/green, rolling y canary nativas y Managed Delivery declarativo. Es potente pero con muchos microservicios propios que operar; Argo CD es pull-based y centrado en Git, con menos piezas. Valorar coste operativo según D16 (sin licencias de pago por defecto; Spinnaker es OSS).

| Aspecto | Argo CD + Rollouts (D21) | Spinnaker |
|---|---|---|
| Modelo | Estado deseado en Git, pull | Pipelines con stages |
| Canary | AnalysisTemplate en el clúster | Estrategias nativas; análisis automatizado de canary |
| Operación | Pocos controladores | Varios servicios propios |

## Ejemplos
### Mal
```text
Pipeline Spinnaker que hace "kubectl apply" a prod en paralelo a Argo CD sobre el mismo namespace.
```
### Bien
```text
Spinnaker (heredado) limitado a app legacy "billing-vm"; servicios nuevos: repo GitOps + Argo CD + Rollouts.
Plan de migración: ADR + hoja de ruta por servicio.
```

## Criterios de decisión y trampas
### Cómo decidir
- Argo CD y Rollouts por defecto; Spinnaker solo para un caso que ellos no cubran y con ADR.
- Si se hereda, acota su ámbito y planifica migrar a manifiestos declarativos.
### Trampas frecuentes
- Introducir una plataforma pesada para un canary que ya cubre Rollouts.
- Pipelines de Spinnaker sin versionar en Git.
- Credenciales de cuentas cloud de larga vida.
- Dos fuentes de verdad para el mismo despliegue.
- Sin plan de salida.
### Evidencia
- Un ADR con el caso que justifica la herramienta y el plan de salida.

## Checklist de revisión
- [ ] Existe ADR si se usa Spinnaker.
- [ ] Sin doble gestión del mismo recurso.
- [ ] Hoja de ruta de migración si es heredado.

## Enforcement
Revisión humana (decisión de arquitectura en ADR). Sin artefacto automático.

## Relacionados, fuentes y mantenimiento
- Relacionados: `argo-cd`, `argo-rollouts`, `flux-comparison`, `strangler-fig-migration`.
- Fuentes (2026-11-07): https://spinnaker.io/docs/concepts/ · ADR-0021.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T3
