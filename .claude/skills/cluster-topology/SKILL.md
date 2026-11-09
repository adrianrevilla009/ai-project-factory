---
name: cluster-topology
description: "Usar al decidir cuántos clústeres Kubernetes, por entorno/región/cell, y qué va en cada uno antes de definir infraestructura EKS o local (kind/k3d)."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Topología de clústeres

## Cuándo aplicar y cuándo no
- Aplica al diseñar el reparto de clústeres (entornos, regiones, cells, plataforma vs. aplicaciones) en un proyecto generado.
- No aplica a la topología de red/VPC (ver bloque de redes) ni al reparto interno por namespaces (ver `namespaces-quotas-multitenancy`).

## Reglas
- **MUST** separar producción de no-producción en clústeres distintos (el límite de blast radius es el clúster, no el namespace).
- **MUST** documentar en un ADR del proyecto el número de clústeres, su propósito y el criterio de crecimiento.
- **MUST** definir cada clúster como código (Terraform para EKS, ver `eks-networking`); **MUST NOT** crear clústeres a mano.
- **SHOULD** empezar con el mínimo: un clúster por entorno (dev, staging, prod) y añadir regiones/cells solo con requisito de RTO/RPO o residencia de datos.
- **SHOULD** alojar las herramientas de plataforma (GitOps, observabilidad, Vault) en un clúster o cuenta de gestión propio si el proyecto lo justifica.
- **SHOULD** usar nombres predecibles: `<proyecto>-<entorno>-<region>`.
- **MUST** declarar qué NO se reproduce en local: kind/k3d son un único nodo/clúster; sin zonas de disponibilidad reales, sin balanceador cloud, sin IAM de nube.
- **MUST NOT** afirmar "listo para producción en AWS": estado = preparado para AWS, no verificado en real (ADR-0004).

## Por qué
Los fallos de plano de control, upgrades y cuotas afectan a todo el clúster. Pocos clústeres grandes reducen coste y operación; muchos pequeños reducen blast radius. La decisión debe ser explícita y revisable, no accidental.

## Ejemplos
### Mal
```text
1 clúster "k8s" con namespaces dev, staging y prod compartiendo nodos y CRDs.
```
### Bien
```yaml
# docs/adr/0007-cluster-topology.md (extracto)
clusters:
  - name: shop-dev-euw1      # purpose: dev + previews efimeros
  - name: shop-stg-euw1      # purpose: staging, paridad con prod
  - name: shop-prod-euw1     # purpose: produccion, region primaria
  - name: shop-prod-euc1     # purpose: DR, activar solo si RTO < 1h (ver multi-cluster-and-dr)
local: kind (1 clúster, sin AZ; no reproduce LB, IAM ni multi-AZ)
```

## Checklist de revisión
- [ ] Prod y no-prod en clústeres separados.
- [ ] ADR con propósito y criterio de crecimiento por clúster.
- [ ] Clústeres definidos en Terraform, no manualmente.
- [ ] Limitaciones del entorno local declaradas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de ADR de topología | 3 | agente `architect-reviewer` (pendiente de verificar nombre) |
| Aprobación de la decisión | 4 | revisión humana en gate de arquitectura |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `multi-cluster-and-dr`, `multi-cluster-mesh`, `cell-based-architecture`, `eks-networking`.
- Fuentes: documentación de Kubernetes (cluster architecture) y guías de EKS best practices.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
