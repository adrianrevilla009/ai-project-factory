---
name: operators
description: "Usar al adoptar operators en Kubernetes (CloudNativePG para Postgres, Strimzi para Kafka): criterios de elección, CRDs, upgrades y operación segura."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Operators (CloudNativePG, Strimzi)

## Cuándo aplicar y cuándo no
- Aplica al decidir y operar bases de datos o brokers dentro de Kubernetes con un operator OSS (CloudNativePG, Strimzi).
- No aplica a servicios gestionados de nube (RDS, MSK): ver las skills de bloques de datos/mensajería y la matriz AWS-local.

## Reglas
- **MUST** decidir en un ADR si el estado va en operator o en servicio gestionado; el criterio incluye RTO/RPO, equipo y coste operativo.
- **MUST** usar operators con licencia OSS (CloudNativePG, Strimzi); **MUST NOT** introducir operators de pago por defecto (D16).
- **MUST** instalar el operator en su propio namespace y los clústeres de datos en el namespace del servicio.
- **MUST** fijar la versión del operator y de sus CRDs; revisar notas de release antes de actualizar, y actualizar CRDs de forma controlada (Helm no actualiza CRDs de `crds/` por defecto).
- **MUST** definir para cada clúster: réplicas en AZ distintas (anti-affinity/topology spread), `PodDisruptionBudget`, resources, almacenamiento (StorageClass) y backups probados (ver `backup-and-restore`).
- **MUST NOT** ejecutar una única réplica de base de datos o broker en prod.
- **SHOULD** exponer métricas del operator y del clúster a Prometheus y alertar sobre lag de réplica y estado del clúster.
- **SHOULD** probar el failover y la restauración en un entorno no productivo antes de confiar en ellos.
- **MUST** respetar la regla de no doble escritura Postgres+NoSQL (4.5).
- Local: kind ejecuta los operators, pero no reproduce volúmenes EBS, multi-AZ ni rendimiento real.

## Por qué
Un operator automatiza la operación (failover, backups, upgrades) pero traslada la responsabilidad al equipo: el estado en Kubernetes exige disciplina sobre almacenamiento, backups y upgrades que un servicio gestionado oculta.

## Ejemplos
### Mal
```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata: { name: orders-db }
spec: { instances: 1 }   # sin backup, sin resources, sin spread
```
### Bien
```yaml

apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata: { name: orders-db, namespace: shop-orders-prod }
spec:
  instances: 3
  storage: { size: 50Gi }
  resources:
    requests: { cpu: "1", memory: 4Gi }
    limits: { memory: 4Gi }
  topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: topology.kubernetes.io/zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector: { matchLabels: { cnpg.io/cluster: orders-db } }
```

## Checklist de revisión
- [ ] ADR operator vs gestionado.
- [ ] Versiones de operator/CRDs fijadas.
- [ ] 3 instancias en AZ distintas y PDB.
- [ ] Backup y restauración probados.
- [ ] Métricas y alertas activas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de manifiestos de operators | 3 | agente revisor de manifiestos |
| Decisión operator vs gestionado | 4 | revisión humana |

Policy automática de réplicas mínimas: pendiente.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `backup-and-restore`, `workload-baseline`, `cluster-upgrades-and-drift`, `db-testing`.
- Fuentes: documentación de CloudNativePG y Strimzi.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
