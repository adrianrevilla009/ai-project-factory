---
name: node-pools-and-capacity
description: "Usar al definir node pools/grupos de nodos, tamaños, taints, spot vs on-demand y headroom de capacidad de un clúster Kubernetes (EKS)."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Node pools y capacidad

## Cuándo aplicar y cuándo no
- Aplica a la definición de grupos de nodos (managed node groups, Karpenter NodePools u otro) y su dimensionado.
- No aplica al autoescalado de pods (ver `autoscaling`) ni al coste agregado (ver `cost-visibility`).

## Reglas
- **MUST** separar al menos: pool de sistema (addons, CoreDNS, controladores) y pool(s) de aplicación.
- **MUST** repartir cada pool en 3 zonas de disponibilidad cuando el entorno lo permita; **MUST NOT** fijar un pool a una sola AZ en prod.
- **MUST** usar taints/tolerations o `nodeSelector` para cargas especiales (GPU, batch, spot); el pool de sistema lleva taint para que no lo ocupen apps.
- **MUST** dejar headroom explícito (p. ej. 20-30 % de capacidad libre, valor a justificar) para absorber la pérdida de una AZ y picos antes de que escale.
- **SHOULD** usar spot/preemptibles solo para cargas tolerantes a interrupción (stateless, con PDB y `terminationGracePeriodSeconds` adecuado); **MUST NOT** ponerles bases de datos ni brokers.
- **SHOULD** preferir pocos tipos de instancia homogéneos por pool para que requests y bin-packing sean predecibles.
- **SHOULD** declarar `--max-pods`/límites de IP por nodo y comprobar que la red de pods no se agota (ver `eks-networking`).
- **MUST** definir los pools como código (Terraform); revisar versión de AMI/kubelet junto con `cluster-upgrades-and-drift`.
- Local: kind/k3d no reproduce pools, AZ ni spot; se simula con labels en nodos de prueba.

## Por qué
Un pool único mezcla addons críticos con apps ruidosas: un despliegue mal dimensionado deja sin DNS al clúster. El headroom y las AZ determinan si perder una zona es un incidente o un evento normal.

## Ejemplos
### Mal
```hcl
node_groups = { default = { instance_types = ["m5.large"], min_size = 1, max_size = 50, subnet_ids = [var.subnet_a] } }
```
### Bien
```hcl
# atributos de primer nivel contrastados con el provider AWS el 2026-11-08
node_groups = {
  system = { instance_types = ["m6i.large"], min_size = 3, max_size = 3,
             subnet_ids = var.private_subnet_ids_3az,
             taints = [{ key = "CriticalAddonsOnly", value = "true", effect = "NO_SCHEDULE" }] }
  apps   = { instance_types = ["m6i.xlarge"], min_size = 3, max_size = 30,
             subnet_ids = var.private_subnet_ids_3az, labels = { pool = "apps" } }
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Grupos de nodos por perfil de carga (propósito general, memoria, GPU, sistema) con etiquetas y tolerancias; capacidad con autoescalado y margen.
- Mezcla instancias de distinto tipo con cuidado y prueba la interrupción.
### Trampas frecuentes
- Un único tipo de nodo para todo.
- Sin margen: un despliegue deja el clúster sin capacidad.
- Cargas críticas en nodos que se pueden interrumpir.
- Límites de recursos que no se corresponden con el uso real.
- Autoescalado sin límites máximos.
### Evidencia
- Una prueba de escalado y de pérdida de un nodo con las cargas críticas en pie.

## Checklist de revisión
- [ ] Pool de sistema separado y con taint.
- [ ] Pools multi-AZ (3) en prod.
- [ ] Headroom y justificación documentados.
- [ ] Spot solo para cargas tolerantes.
- [ ] Definido en Terraform.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de IaC de pools | 3 | agente revisor de IaC |
| Dimensionado y headroom | 4 | revisión humana |

Checks automáticos de IaC: pendiente (`policies/iac-checks/`).

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `cluster-topology`, `autoscaling`, `workload-baseline`, `eks-networking`, `cost-visibility`.
- Fuentes: documentación EKS (managed node groups) y Karpenter.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
