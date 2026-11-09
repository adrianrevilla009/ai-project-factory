---
name: multi-cluster-and-dr
description: "Usar al diseñar recuperación ante desastres o despliegue multi-clúster/multi-región en Kubernetes: patrones activo-pasivo y activo-activo, estado y conmutación."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Multi-clúster y DR

## Cuándo aplicar y cuándo no
- Aplica cuando el RTO/RPO o la residencia de datos exigen más de un clúster o región.
- No aplica si un solo clúster multi-AZ cumple los objetivos; ver `cluster-topology` y `tier-model-and-rpo-rto`. La malla multi-clúster va en `multi-cluster-mesh`.

## Reglas
- **MUST** partir de los objetivos RTO/RPO por tier de servicio (ver `tier-model-and-rpo-rto`); sin objetivos no se añade complejidad multi-clúster.
- **MUST** elegir patrón por servicio y documentarlo: backup-restore, pilot light, warm standby o activo-activo (ver `multi-region-patterns`).
- **MUST** que el despliegue a todos los clústeres salga del mismo Git (ApplicationSets o equivalente) con diferencias solo en overlays.
- **MUST** resolver primero el estado: replicación de datos con la matriz definida (ver `data-replication-matrix`); **MUST NOT** doble escritura Postgres+NoSQL para "replicar".
- **MUST** diseñar la conmutación (DNS/health checks/Global Accelerator, ver bloque de redes) y el failback con runbook probado.
- **MUST** mantener identidades, secretos y certificados disponibles en el clúster de DR (Vault y Keycloak tienen su propio DR, ver `vault-and-keycloak-dr`).
- **SHOULD** ensayar la conmutación en game days (tabletop, ver `fault-injection-and-game-days`) y medir RTO.
- **SHOULD** evitar acoplar los clústeres: el fallo de uno no debe depender del plano de control del otro.
- **MUST NOT** afirmar "listo para producción en AWS" ni resiliencia multi-región verificada: la fábrica no despliega; estado = preparado para AWS, no verificado en real.
- Local: dos clústeres kind solo simulan el reparto; no reproducen latencia entre regiones ni fallos de región.

## Por qué
Multi-clúster duplica coste y complejidad operativa. Solo compensa si el negocio lo exige, y entonces el cuello de botella real es el estado y la conmutación, no los manifiestos.

## Ejemplos
### Mal
```text
"Tenemos dos clústeres, asi que hay DR": datos solo en la region A, sin runbook, sin prueba.
```
### Bien
```yaml
# docs/dr/orders-dr.yaml (decision por servicio)
service: orders
tier: 1
rpo: 5m
rto: 30m
pattern: warm-standby
clusters: { primary: shop-prod-euw1, standby: shop-prod-euc1 }
data: { postgres: "replica en standby (ver data-replication-matrix)", kafka: "mirror async, aceptar perdida RPO" }
failover: "runbook failover-orders.md; ensayo trimestral"
```

## Checklist de revisión
- [ ] RTO/RPO por servicio y patrón elegido.
- [ ] Mismo Git para todos los clústeres.
- [ ] Estrategia de datos y de identidad/secretos en DR.
- [ ] Runbook de failover y failback ensayado.
- [ ] Sin afirmaciones de verificación real en AWS.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión del documento de DR por servicio | 3 | agente revisor de arquitectura |
| Aprobación del patrón y del coste | 4 | revisión humana |

Validador automático de documento DR: pendiente.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `cluster-topology`, `backup-and-restore`, `multi-cluster-mesh`, `istio-multicluster-tradeoffs`, `eks-multi-region-and-argo-cd-multicluster`.
- Fuentes: documentación de Kubernetes y guías de resiliencia/DR de AWS (Well-Architected, Reliability Pillar).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
