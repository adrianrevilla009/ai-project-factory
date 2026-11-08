---
name: jvm-observability
description: "Usar al definir qué observar de la JVM en producción: memoria, GC, hilos, pools, JFR y volcados, en contenedores Kubernetes."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Observabilidad de la JVM

## Cuándo aplicar y cuándo no
- Aplica a dashboards, alertas y diagnóstico de memoria, GC, hilos y pools de un servicio Java en Kubernetes.
- No aplica al ajuste de flags de memoria (ver `jvm-in-containers`) ni a profiling puntual (`profiling-and-leaks`).

## Reglas
- **MUST** exponer las métricas de JVM de Micrometer (`jvm.memory.*`, `jvm.gc.*`, `jvm.threads.*`, `jvm.classes.*`) y las del pool de conexiones (Hikari).
- **MUST** tener un dashboard por servicio con: heap usado tras GC, pausas de GC, hilos vivos/bloqueados, utilización de pools, CPU y throttling del contenedor.
- **MUST** relacionar memoria de la JVM con el `limit` del contenedor: alertar por cercanía de OOMKilled, no solo por heap.
- **MUST** habilitar `-XX:+HeapDumpOnOutOfMemoryError` con ruta a un volumen efímero con espacio; **MUST NOT** subir volcados a sitios sin control de acceso (contienen datos).
- **SHOULD** usar JFR (continuo, de bajo overhead) para diagnóstico bajo demanda en lugar de agentes de profiling permanentes.
- **SHOULD** exponer métricas de executors (`ExecutorServiceMetrics`) y de hilos virtuales o pinning si se usan (comprobar qué eventos JFR).
- **MUST NOT** alertar por uso de heap bruto; alertar por síntoma (latencia, errores) y usar la JVM como diagnóstico.
- **SHOULD** registrar `jvm.info` / versión de JDK como atributo para correlacionar regresiones con upgrades.

## Por qué
El heap "alto" suele ser normal (GC lazy); lo que importa es el heap tras GC, el tiempo en pausa y la presión en el límite del contenedor. Sin volcado automático, un OOM en producción no se puede analizar. Las alertas basadas en causas generan ruido (ver `alerting-symptom-based`).

## Ejemplos
### Mal
```yaml
# Alerta por causa interna, ruidosa
- alert: HeapHigh
  expr: jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.8
```
### Bien
```yaml
# Panel de diagnóstico (no página): presión de GC
- record: job:jvm_gc_pause_seconds:rate5m
  expr: sum by (job) (rate(jvm_gc_pause_seconds_sum[5m]))
# Riesgo de OOMKilled: memoria de trabajo frente al límite del contenedor
- alert: ContainerNearMemoryLimit
  expr: |
    max by (pod) (container_memory_working_set_bytes{container="app"})
      / max by (pod) (kube_pod_container_resource_limits{resource="memory",container="app"}) > 0.9
  for: 10m
  labels: { severity: ticket }
```
```text
JAVA_TOOL_OPTIONS=-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/dumps
```

## Checklist de revisión
- [ ] Dashboard de JVM y pools por servicio.
- [ ] Memoria comparada con el límite del contenedor.
- [ ] Volcado en OOM a volumen controlado.
- [ ] Sin alertas paginables por heap bruto.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de dashboards y reglas de alerta como código | 3 | agente `code-reviewer` |
| Validación de reglas con `promtool` en CI (pendiente) | 1 | pipeline del proyecto generado (pendiente) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `jvm-in-containers`, `profiling-and-leaks`, `metrics-micrometer`, `connection-pooling`, `virtual-threads`.
- Fuentes: documentación de Micrometer (JVM metrics) y de OpenJDK/JFR, consultadas 2026-11-07; comprobar nombres exactos en la versión usada.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
