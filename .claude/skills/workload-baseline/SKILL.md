---
name: workload-baseline
description: "Usar al escribir o revisar Deployments/StatefulSets: requests/limits, probes, PDB, topology spread y seccomp RuntimeDefault para servicios Spring Boot."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Baseline de workloads

## Cuándo aplicar y cuándo no
- Aplica a todo Deployment/StatefulSet de aplicación (Java + Spring Boot) en cualquier entorno.
- No aplica a Jobs puntuales ni a controladores de terceros (operators) cuyo chart ya define su baseline; revisar igualmente requests y seccomp.

## Reglas
- **MUST** definir `resources.requests` de cpu y memory y `limits.memory` en cada contenedor; la memoria request = limit en servicios JVM (evita OOM por overcommit).
- **SHOULD** no fijar `limits.cpu` salvo razón medida (el throttling degrada la latencia); decisión documentada.
- **MUST** definir `readinessProbe` y `livenessProbe` (y `startupProbe` si el arranque es lento) apuntando a los endpoints de Actuator (ver `actuator-and-health`); la liveness **MUST NOT** depender de dependencias externas.
- **MUST** tener `PodDisruptionBudget` para todo servicio con `replicas >= 2`.
- **MUST** usar `topologySpreadConstraints` por zona (`topology.kubernetes.io/zone`) y por nodo en servicios con varias réplicas.
- **MUST** fijar `seccompProfile.type: RuntimeDefault`, `runAsNonRoot`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]` (ver `container-and-k8s-security`).
- **MUST** configurar `terminationGracePeriodSeconds` y apagado ordenado (`server.shutdown=graceful`).
- **MUST NOT** usar tag `latest`; fijar versión o digest.
- **SHOULD** mínimo 2 réplicas en prod.

## Por qué
Sin requests el scheduler no puede decidir ni el autoscaler calcular; sin probes el tráfico llega a pods no listos; sin PDB un drain de nodo tira todas las réplicas; sin spread, una AZ caída se lleva el servicio entero.

## Ejemplos
### Mal
```yaml
containers:
  - name: orders
    image: registry.example.com/orders:latest
```
### Bien
```yaml
spec:
  replicas: 3
  template:
    spec:
      securityContext: { runAsNonRoot: true, seccompProfile: { type: RuntimeDefault } }
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: ScheduleAnyway
          labelSelector: { matchLabels: { app: orders } }
      containers:
        - name: orders
          image: registry.example.com/orders:1.4.2
          resources:
            requests: { cpu: 500m, memory: 1Gi }
            limits: { memory: 1Gi }
          readinessProbe: { httpGet: { path: /actuator/health/readiness, port: 8080 } }
          livenessProbe: { httpGet: { path: /actuator/health/liveness, port: 8080 } }
          securityContext: { allowPrivilegeEscalation: false, capabilities: { drop: [ALL] } }
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: orders }
spec:
  maxUnavailable: 1
  selector: { matchLabels: { app: orders } }
```

## Checklist de revisión
- [ ] requests/limits en todos los contenedores.
- [ ] Probes con endpoints de Actuator; liveness sin dependencias externas.
- [ ] PDB y topology spread presentes.
- [ ] seccomp RuntimeDefault y securityContext restringido.
- [ ] Imagen sin `latest`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Kyverno: resources, probes, seccomp, sin latest (modo Audit) | 1 | `policies/kyverno/workload-baseline.yaml` |
| PDB y topology spread | 3 | revisión de manifiestos (regla Kyverno pendiente) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `actuator-and-health`, `container-and-k8s-security`, `pod-security-and-admission`, `autoscaling`.
- Fuentes: documentación de Kubernetes (probes, PDB, topology spread) y Kyverno — TODO-VERIFY versión, 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
