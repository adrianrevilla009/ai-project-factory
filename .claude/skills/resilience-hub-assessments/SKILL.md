---
name: resilience-hub-assessments
description: "Usar al preparar una evaluación de resiliencia con AWS Resilience Hub: política RTO/RPO por tier, recomendaciones y cómo tratarlas como diseño, no como prueba."
metadata:
  block: "19-resilience-dr-finops"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Evaluaciones con AWS Resilience Hub

## Cuándo aplicar y cuándo no
- Aplica cuando un proyecto tenga infraestructura real en AWS y se quiera validar RTO/RPO; en la fábrica se prepara el diseño.
- No aplica sin recursos desplegados: Resilience Hub evalúa recursos existentes. La fábrica no despliega (D4).
- No sustituye ejercicios (`fault-injection-and-game-days`).

## Reglas
- **MUST** expresar la política de resiliencia de cada tier (RTO/RPO por fallo de aplicación, infraestructura, AZ y región) en un fichero versionado del proyecto, coherente con `tier-model-and-rpo-rto`.
- **MUST** tratar el resultado como estimación basada en configuración, no como medición; **MUST NOT** usarla para afirmar que un RTO "está probado".
- **SHOULD** definir la aplicación por pila Terraform/tags para que el inventario sea reproducible.
- **SHOULD** convertir cada recomendación en issue con prioridad y dueño, o en riesgo aceptado documentado.
- **SHOULD** repetir la evaluación tras cambios relevantes y antes de cada revisión anual de tier.
- **MUST** validar que el coste de las recomendaciones cabe en el presupuesto (`finops-of-resilience`).
- **MUST NOT** aplicar recomendaciones sin pasar por PR y revisión de IaC.

## Por qué
La herramienta ayuda a descubrir faltas de redundancia que a mano pasan inadvertidas (p. ej. un recurso sin réplica en otra región) y a seguir el cumplimiento de la política. Pero su veredicto parte de la configuración, no de ver un failover real. El whitepaper de DR la cita para validar de forma continua si se cumplen RTO y RPO.

## Ejemplos
### Mal
```text
"Resilience Hub dice 'Policy met': RTO de 45 min garantizado."
```
### Bien
```yaml
# resilience-policy-tier1.yaml (documento del proyecto; la política se crea en la herramienta)
tier: 1
targets:
  application: { rto: 1h,  rpo: 5m }
  infrastructure: { rto: 1h, rpo: 5m }
  az: { rto: 5m, rpo: 0 }
  region: { rto: 1h, rpo: 5m }
review: "Estimación de configuración; el RTO real se mide en game day"
```

## Checklist de revisión
- [ ] Política por tier versionada y alineada con `resilience.yaml`.
- [ ] Recomendaciones convertidas en issues o riesgos aceptados.
- [ ] El informe no se cita como prueba de RTO.
- [ ] Coste de las mejoras estimado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión del informe y del seguimiento | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tier-model-and-rpo-rto`, `fault-injection-and-game-days`, `dependency-mapping-and-blast-radius`, `finops-of-resilience`.
- Fuente: DR whitepaper (https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-options-in-the-cloud.html, 2026-11-07). Detalles de la política y fuentes de importación.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
