---
name: autoscaling
description: "Usar al configurar HPA, VPA o KEDA para escalar pods Spring Boot por CPU, memoria, métricas propias o eventos (colas Kafka), junto al autoscaler de nodos."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Autoscaling (HPA, VPA, KEDA)

## Cuándo aplicar y cuándo no
- Aplica a la política de escalado horizontal y vertical de workloads.
- No aplica al dimensionado de nodos (ver `node-pools-and-capacity`) ni a la capacidad planificada (ver `capacity-and-load-modeling`).

## Reglas
- **MUST** que el workload tenga `resources.requests` correctos antes de activar HPA: el porcentaje se calcula sobre requests.
- **MUST** definir `minReplicas >= 2` en prod y `maxReplicas` acotado por cuota y presupuesto.
- **MUST NOT** combinar HPA y VPA sobre la misma métrica (cpu/memory) del mismo workload; VPA en modo `Off`/recomendación si coexisten.
- **SHOULD** usar HPA `autoscaling/v2` con `behavior` (estabilización de bajada, límites de subida) para evitar flapping.
- **SHOULD** escalar con KEDA por eventos (lag de consumer group Kafka, longitud de cola) en consumidores; el máximo de réplicas **MUST NOT** superar las particiones del topic.
- **MUST** considerar el arranque JVM: usar `startupProbe` y warm-up; escalar tarde por arranque lento es un riesgo.
- **MUST** que el escalado de pods tenga nodos disponibles (Cluster Autoscaler/Karpenter) y headroom; si no, los pods quedan `Pending`.
- **SHOULD** validar con pruebas de carga (ver `performance-gate`) que el escalado responde antes de saturar.
- Local: kind no reproduce autoscaling de nodos; metrics-server y KEDA sí pueden instalarse.

## Por qué
Un HPA sobre requests mal fijados escala de más o de menos. HPA y VPA peleando por CPU provocan oscilación. Un consumidor Kafka escalado más allá de las particiones solo gasta recursos.

## Ejemplos
### Mal
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  minReplicas: 1
  maxReplicas: 500
  metrics: [{ type: Resource, resource: { name: cpu, target: { type: Utilization, averageUtilization: 20 } } }]
```
### Bien
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: orders, namespace: shop-orders-prod }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: orders }
  minReplicas: 3
  maxReplicas: 12
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
  behavior:
    scaleDown: { stabilizationWindowSeconds: 300 }
```
```yaml
# KEDA (comprobar apiVersion y campos segun version instalada)
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
spec:
  scaleTargetRef: { name: orders-consumer }
  minReplicaCount: 2
  maxReplicaCount: 6          # = particiones del topic
  triggers:
    - type: kafka
      metadata: { topic: orders, consumerGroup: orders-consumer, lagThreshold: "100", bootstrapServers: kafka.example.svc:9092 }
```

## Checklist de revisión
- [ ] Requests correctos antes de HPA.
- [ ] min >= 2 y max acotado.
- [ ] Sin HPA y VPA sobre la misma métrica.
- [ ] max de consumidores <= particiones.
- [ ] Capacidad de nodos validada.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de HPA/ScaledObject | 3 | agente revisor de manifiestos |
| Prueba de carga con escalado | 3 | `performance-gate` (pipeline) |

Policy Kyverno de `minReplicas`: pendiente.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `node-pools-and-capacity`, `workload-baseline`, `backpressure-and-bulkheads`, `capacity-and-load-modeling`.
- Fuentes: Kubernetes (HPA), VPA y KEDA docs (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
