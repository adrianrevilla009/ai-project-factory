---
name: eks-multi-region-and-argo-cd-multicluster
description: "Usar al diseñar EKS en varias regiones y su entrega GitOps con Argo CD multicluster: topología, ApplicationSets, estado y fallo del plano de control."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# EKS multi-región y Argo CD multicluster

## Cuándo aplicar y cuándo no
- Aplica cuando el tier de RPO/RTO (`tier-model-and-rpo-rto`) exige más de una región y la plataforma es EKS + GitOps.
- No aplica a servicios de tier bajo (un clúster multi-AZ basta) ni al diseño de la malla (ver `istio-multicluster-tradeoffs`).
- Diseño en papel: preparado para AWS, no verificado en real. La fábrica no despliega (ADR-0004).

## Reglas
- **MUST** tratar cada región como un clúster EKS independiente (no existe un clúster que abarque regiones); la unidad de fallo es el clúster.
- **MUST** declarar el modelo: activo-activo, activo-pasivo (warm standby) o pilot light, y su coste (`finops-of-resilience`).
- **MUST** definir el clúster como código Terraform parametrizado por región, sin diferencias manuales entre regiones.
- **MUST** usar `ApplicationSet` con el generador `cluster` y labels (`env`, `region`, `tier`) en vez de una `Application` copiada por clúster.
- **MUST** decidir y documentar el modelo de Argo CD: instancia por clúster (blast radius pequeño, más operación) o hub que gestiona clústeres remotos (un punto de fallo y de privilegio).
- **MUST NOT** alojar el único Argo CD en la región que puede fallar; el plano GitOps debe poder reconciliar la región superviviente.
- **MUST NOT** replicar estado de aplicación mediante Argo CD; el estado sigue la matriz de `data-replication-matrix`.
- **SHOULD** desplegar por oleadas (región canaria primero) con `sync-wave`/progressive sync; ver `change-and-release-management`.
- **SHOULD** mantener imágenes en un registro accesible desde ambas regiones (Harbor/ECR con réplica).

## Por qué
Un clúster regional que cae arrastra su Argo CD si está dentro. Las copias manuales de manifiestos divergen y el failover descubre la divergencia. El generador `cluster` crea una Application por clúster registrado y expone `name`, `server` y labels como parámetros, así que añadir una región es registrar un clúster con labels.

## Ejemplos
### Mal
```yaml
# Application duplicada a mano; el destino está fijo
kind: Application
spec:
  destination: {server: https://primary.example.internal}
```
### Bien
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: {name: orders}
spec:
  generators:
    - clusters:
        selector:
          matchLabels: {env: prod, tier: "1"}
  template:
    metadata: {name: "orders-{{nameNormalized}}"}
    spec:
      project: default
      source:
        repoURL: https://git.example.internal/platform/orders.git
        path: "overlays/{{metadata.labels.region}}"
        targetRevision: main
      destination: {server: "{{server}}", namespace: orders}
```
Nota: el clúster local por defecto no tiene Secret y no lo selecciona el generador.

## Criterios de decisión y trampas
### Cómo decidir
- Un clúster de gestión o una instancia por región según el riesgo; define cómo se despliega a cada clúster y cómo se propaga la configuración.
- Los registros de imágenes y la identidad deben existir en ambas regiones.
### Trampas frecuentes
- Un único plano de entrega que cae con una región.
- Sin réplica de imágenes en la región secundaria.
- Credenciales de clúster con permisos amplios.
- Despliegues simultáneos a todas las regiones sin escalonar.
- Sin ensayo de despliegue con una región caída.
### Evidencia
- Un despliegue de prueba con una región indisponible.

## Checklist de revisión
- [ ] Modelo (activo-activo / warm standby / pilot light) y tier justificados.
- [ ] Argo CD no depende de la región que falla.
- [ ] ApplicationSet con labels; sin Applications duplicadas.
- [ ] Orden de despliegue por región documentado.
- [ ] Estado de datos fuera del alcance de GitOps.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Rego/Conftest: prohibir `Application` con `destination.server` literal en repos de entrega | 1 | pendiente: `policies/opa-conftest/` |
| Revisión humana del diseño multi-región y del gate de arquitectura | 4 | PR / gate |

## Relacionados, fuentes y mantenimiento
- Relacionados: `multi-region-patterns`, `failover-and-failback-runbooks`, `istio-multicluster-tradeoffs`, `dependency-mapping-and-blast-radius`.
- Fuentes (verificado 2026-11-07): https://argo-cd.readthedocs.io/en/stable/operator-manual/applicationset/Generators-Cluster/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
