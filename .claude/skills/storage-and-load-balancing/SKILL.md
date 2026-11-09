---
name: storage-and-load-balancing
description: "Usar al elegir almacenamiento persistente (CSI) y balanceo de carga (LoadBalancer, ingress) en clústeres Kubernetes on-prem sin servicios del proveedor cloud."
metadata:
  block: "21-on-prem-hybrid"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Almacenamiento y balanceo on-prem

## Cuándo aplicar y cuándo no
- Aplica a clústeres propios donde no existen `StorageClass` ni `Service type=LoadBalancer` provistos por una nube.
- No aplica a la matriz AWS↔local: aquí NO se reproduce EBS/EFS/ELB; se usan equivalentes OSS con semántica distinta (rendimiento, durabilidad y fallos difieren). Referencia T3.

## Reglas
- **MUST** usar un driver CSI con `StorageClass` explícita; declarar `reclaimPolicy` y `volumeBindingMode: WaitForFirstConsumer` para respetar topología.
- **MUST** documentar el modelo de replicación y durabilidad del almacenamiento elegido (p. ej. Ceph/Rook, Longhorn) y probar la pérdida de un nodo.
- **MUST** respaldar volúmenes con VolumeSnapshots y copia externa; la réplica no es backup.
- **MUST** una solución de LoadBalancer bare-metal (p. ej. MetalLB) con rangos de IP reservados y documentados. Comprobar modo (L2/BGP) según la red.
- **SHOULD** usar Gateway API (`gateway-api`) para entrada de tráfico.
- **MUST NOT** usar `hostPath` para datos de aplicación.

## Por qué
Sin la nube, nadie aporta durabilidad ni IPs flotantes: hay que diseñarlas, y los fallos se descubren tarde si no se ensayan.

## Ejemplos
### Mal
```yaml
volumes:
  - name: data
    hostPath: { path: /data }
```
### Bien
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: replicated-ssd }
provisioner: example.csi.vendor.io
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer
```

## Criterios de decisión y trampas
### Cómo decidir
- Clase de almacenamiento por perfil de carga con rendimiento, replicación y copia conocidos; balanceo de entrada con alta disponibilidad real.
- Pruebas de fallo del almacenamiento.
### Trampas frecuentes
- Almacenamiento local sin replicación para datos que importan.
- Un balanceador único.
- Rendimiento no medido.
- Sin copia de los volúmenes.
- Direcciones fijas sin gestión.
### Evidencia
- Una prueba de fallo de nodo con los datos y el tráfico recuperados.

## Checklist de revisión
- [ ] StorageClass con reclaimPolicy y binding mode.
- [ ] Snapshots y backup externo probados.
- [ ] LoadBalancer con rangos de IP documentados.
- [ ] Sin `hostPath` en cargas de aplicación.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Kyverno que prohíba `hostPath` | 1 | pendiente (`policies/kyverno/`) |
| Revisión de diseño de almacenamiento | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `kubernetes-on-prem`, `gateway-api`, `container-and-k8s-security`.
- Fuentes: https://kubernetes.io/docs/concepts/storage/storage-classes/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T3
