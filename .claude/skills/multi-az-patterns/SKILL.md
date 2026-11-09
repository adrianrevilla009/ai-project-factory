---
name: multi-az-patterns
description: "Usar al diseñar o revisar alta disponibilidad dentro de una región AWS: nodos EKS en 3 AZ, topology spread, PDB y datos Multi-AZ (Aurora, MSK, Vault Raft)."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Patrones Multi-AZ

## Cuándo aplicar y cuándo no
- Aplica a todo servicio de tier 0-2 dentro de eu-west-1 (y eu-central-1 para la copia secundaria).
- No aplica a fallo de región (ver `multi-region-patterns`). Tier 3 puede aceptar una sola AZ si está documentado.
- Diseño: preparado para AWS, no verificado en real. En local (kind/k3d, Redis) **no se reproduce** Multi-AZ real ni autoscaling de nodos.

## Reglas
- **MUST** repartir nodos de EKS en 3 AZ y usar `topologySpreadConstraints` por `topology.kubernetes.io/zone` en cada Deployment con más de 1 réplica.
- **MUST** definir un `PodDisruptionBudget` por servicio con `minAvailable` o `maxUnavailable` coherente con las réplicas.
- **MUST** usar Aurora Multi-AZ (instancia lectora en otra AZ), MSK en 3 AZ con `min.insync.replicas` >= 2 y `replication.factor` 3, ElastiCache Multi-AZ, Vault Raft con 3 nodos en 3 AZ.
- **MUST** que las réplicas de un servicio no superen la capacidad que queda al perder una AZ (N+1 por AZ): con 3 AZ, dimensionar al 150 % de la carga.
- **SHOULD** usar zonal shift de ARC para sacar una AZ degradada (ver `application-recovery-controller-and-health-checks`).
- **MUST NOT** fijar `nodeSelector`/`nodeAffinity` a una AZ concreta salvo volúmenes EBS zonales justificados.
- **MUST NOT** usar tráfico entre AZ innecesario sin medir su coste (ver `finops-of-resilience`).

## Por qué
Una AZ es el dominio de fallo más frecuente. Sin spread y PDB, el planificador puede colocar todas las réplicas en una AZ o drenar todos los nodos a la vez en una actualización. Los volúmenes EBS son zonales: un pod con PVC queda atado a su AZ.

## Ejemplos
### Mal
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api }
spec:
  replicas: 3
  template:
    spec:
      containers: [{ name: app, image: example.registry/orders-api:1.0.0 }]
```
### Bien
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: orders-api }
spec:
  replicas: 6
  template:
    metadata: { labels: { app: orders-api } }
    spec:
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector: { matchLabels: { app: orders-api } }
      containers: [{ name: app, image: example.registry/orders-api:1.0.0 }]
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: orders-api }
spec:
  minAvailable: 4
  selector: { matchLabels: { app: orders-api } }
```

## Checklist de revisión
- [ ] Nodos en 3 AZ; spread por zona y PDB en cada servicio.
- [ ] Datos con réplica en otra AZ; Vault Raft 3 nodos en 3 AZ.
- [ ] Capacidad suficiente tras perder una AZ.
- [ ] Sin afinidad rígida a una AZ.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Kyverno: exigir PDB y spread en Deployments con replicas > 1 | 1 | pendiente (`policies/kyverno/`) |
| Revisión de manifiestos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `static-stability-and-cell-architecture`, `tier-model-and-rpo-rto`, `multi-region-patterns`.
- Fuentes: Kubernetes, Pod Topology Spread Constraints y PDB (kubernetes.io/docs); AWS Aurora/MSK Multi-AZ.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
