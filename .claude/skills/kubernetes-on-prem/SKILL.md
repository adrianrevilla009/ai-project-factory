---
name: kubernetes-on-prem
description: "Usar al diseñar un clúster Kubernetes propio (on-prem o híbrido) con kubeadm: topología HA, etcd, actualizaciones y respaldos."
metadata:
  block: "21-on-prem-hybrid"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Kubernetes on-prem

## Cuándo aplicar y cuándo no
- Aplica cuando por regulación, latencia o coste el clúster corre en infraestructura propia.
- No aplica si basta un servicio gestionado. Este skill es referencia (T3): la fábrica no despliega nada (ADR-0004).

## Reglas
- **MUST** control plane HA: 3 o más nodos (número impar) detrás de un balanceador estable para `kube-apiserver`; el endpoint del balanceador debe coincidir con `ControlPlaneEndpoint` de kubeadm.
- **MUST** decidir topología etcd (apilado: menos máquinas; externo: más separación y más infraestructura) y documentarlo en un ADR.
- **MUST** copias de seguridad de etcd probadas con restauración periódica.
- **MUST** plan de actualización por versión menor, de una en una, con nodos de prueba primero.
- **SHOULD** CNI con soporte de NetworkPolicy; Istio como malla (D-cerradas).
- **MUST NOT** exponer el API server a Internet sin restricción de red y autenticación OIDC (Keycloak).

## Por qué
Sin proveedor gestionado, la disponibilidad del control plane y el respaldo de etcd son responsabilidad propia; un etcd sin backup probado es un riesgo total.

## Ejemplos
### Mal
```text
kubeadm init                       # un solo control plane, IP de un nodo
```
### Bien
```text
kubeadm init --control-plane-endpoint k8s-api.example.internal:6443 --upload-certs
```
Los flags `--control-plane-endpoint` y `--upload-certs` figuran en la guía oficial de HA con kubeadm.

## Criterios de decisión y trampas
### Cómo decidir
- Elige entre distribución gestionada por el proveedor, autogestionada o servicio híbrido según la capacidad del equipo; el plano de control y los datos de etcd son lo más delicado.
- Planifica actualizaciones y copias desde el principio.
### Trampas frecuentes
- Subestimar la operación del plano de control.
- Un solo nodo de control.
- Sin copia de seguridad de etcd.
- Red y almacenamiento decididos tarde.
- Sin plan de actualización.
### Evidencia
- Un ensayo de pérdida de un nodo de control y de restauración desde copia.

## Checklist de revisión
- [ ] 3+ control planes y balanceador con DNS estable.
- [ ] ADR de topología etcd.
- [ ] Backup de etcd con restauración probada.
- [ ] Plan de upgrades por versión menor.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Revisión de diseño de clúster y DR | 4 | revisión humana (sin artefacto automático; pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `storage-and-load-balancing`, `container-and-k8s-security`, `hybrid-identity-and-networking`.
- Fuentes (verificado 2026-11-07): https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T3
