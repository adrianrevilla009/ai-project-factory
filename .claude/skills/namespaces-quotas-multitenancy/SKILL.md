---
name: namespaces-quotas-multitenancy
description: "Usar al crear namespaces por equipo/servicio/entorno con ResourceQuota, LimitRange, NetworkPolicy por defecto y aislamiento multi-tenant en Kubernetes."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Namespaces, cuotas y multitenancy

## Cuándo aplicar y cuándo no
- Aplica al crear o revisar namespaces y su plantilla de aislamiento.
- No aplica al multitenancy de datos de la aplicación (ver `multi-tenancy`) ni al aislamiento fuerte entre clientes hostiles (requiere clústeres separados, ver `cluster-topology`).

## Reglas
- **MUST** crear un namespace por equipo o servicio y entorno, con labels `team`, `env` y `pod-security.kubernetes.io/enforce`.
- **MUST** aplicar `ResourceQuota` (cpu, memory, pods, y objetos como `services.loadbalancers`) y `LimitRange` con requests/limits por defecto en cada namespace.
- **MUST** aplicar una `NetworkPolicy` default-deny (ingress y egress) y abrir solo lo necesario, incluyendo DNS.
- **MUST** asignar RBAC por namespace a grupos del IdP, no a usuarios (ver `rbac-and-service-accounts`).
- **MUST NOT** desplegar workloads de aplicación en `default` ni en `kube-system`.
- **SHOULD** generar la plantilla de namespace desde un único chart/overlay para que todos nazcan iguales.
- **SHOULD** poner cuotas de objetos (secrets, configmaps) si hay riesgo de abuso.
- **MUST** declarar que namespaces = aislamiento lógico "soft": comparten kernel, nodos y plano de control.

## Por qué
Sin cuota un equipo puede consumir todo el clúster; sin default-deny el movimiento lateral es trivial; sin LimitRange los pods sin requests rompen el scheduling y el autoscaling.

## Ejemplos
### Mal
```yaml
apiVersion: v1
kind: Namespace
metadata: { name: team-a }   # sin labels, sin cuota, sin network policy
```
### Bien
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: shop-orders-prod
  labels:
    team: orders
    env: prod
    pod-security.kubernetes.io/enforce: restricted
---
apiVersion: v1
kind: ResourceQuota
metadata: { name: default, namespace: shop-orders-prod }
spec:
  hard: { requests.cpu: "20", requests.memory: 64Gi, pods: "100" }
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: shop-orders-prod }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

## Criterios de decisión y trampas
### Cómo decidir
- Un espacio de nombres por equipo o entorno con cuotas, límites por defecto y políticas de red; aislamiento adicional (nodos o clústeres) si los inquilinos no confían entre sí.
- Cuotas realistas, revisadas con el uso.
### Trampas frecuentes
- Espacios de nombres sin cuotas: uno consume todo.
- Aislamiento «suave» entre inquilinos con requisitos fuertes.
- Permisos de administración sobre el clúster entero.
- Sin política de red por defecto.
- Cuotas que nunca se ajustan.
### Evidencia
- Una prueba demuestra que un espacio de nombres no puede agotar los recursos de otro.

## Checklist de revisión
- [ ] Labels `team`, `env` y PSA en el namespace.
- [ ] ResourceQuota y LimitRange presentes.
- [ ] NetworkPolicy default-deny con excepciones mínimas (DNS incluido).
- [ ] Nada de aplicación en `default`/`kube-system`.
- [ ] RBAC a grupos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Kyverno: exigir quota/networkpolicy por namespace (generate) | 1 | pendiente en `policies/kyverno/` |
| Revisión de la plantilla de namespace | 3 | agente revisor de manifiestos |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `pod-security-and-admission`, `rbac-and-service-accounts`, `multi-tenancy`, `container-and-k8s-security`.
- Fuentes: documentación de Kubernetes (Resource Quotas, Limit Ranges, Network Policies, multi-tenancy).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
