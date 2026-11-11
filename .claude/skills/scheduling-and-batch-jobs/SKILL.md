---
name: scheduling-and-batch-jobs
description: "Usar al crear tareas programadas o jobs batch (Spring @Scheduled, ShedLock, Quartz, Spring Batch) en servicios con varias réplicas."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Planificación y jobs batch

## Cuándo aplicar y cuándo no
- Aplica a tareas periódicas, cierres, reconciliaciones y procesos por lotes en servicios con más de una réplica.
- No aplica a reacciones a eventos (usar consumidores) ni a carga de ficheros de usuario (ver `import-export-and-bulk-data`). Complementa a `scheduling-and-batch`.

## Reglas
- **MUST** asegurar ejecución única entre réplicas: bloqueo distribuido (ShedLock con `@SchedulerLock`) o CronJob de Kubernetes con `concurrencyPolicy: Forbid`.
- **MUST** fijar `lockAtMostFor` mayor que la duración esperada y, si hay desfase de relojes, `lockAtLeastFor` (semántica en https://github.com/lukas-krecan/ShedLock, 2026-11-07).
- **MUST** diseñar cada ejecución idempotente y reanudable (marca de progreso, no "todo o nada" sin reintento).
- **MUST** usar chunking con commit interval acotado en Spring Batch; configurar skip/retry por excepción explícita (https://docs.spring.io/spring-batch/reference/step/chunk-oriented-processing.html, 2026-11-07).
- **MUST** exponer métricas de job (duración, filas, fallos) y alertar si no se ejecuta.
- **MUST NOT** usar `@Scheduled` sin bloqueo en servicios replicados.
- **MUST NOT** ejecutar trabajo pesado en el hilo del scheduler por defecto; usar un executor acotado.
- **SHOULD** externalizar el cron a configuración y fijar zona horaria explícita (`zone = "UTC"`).
- **SHOULD** elegir CronJob de Kubernetes para jobs largos aislados y ShedLock para tareas cortas dentro del servicio.

## Por qué
Con N réplicas, un `@Scheduled` corre N veces: cobros duplicados, correos repetidos. Un job no idempotente convierte un reintento en un incidente. Versiones de ShedLock/Spring Batch.

## Ejemplos
### Mal
```java
@Scheduled(cron = "0 0 2 * * *")
public void closeDay() { ledger.closeAll(); } // corre en cada réplica
```
### Bien
```java
@Scheduled(cron = "0 0 2 * * *", zone = "UTC")
@SchedulerLock(name = "closeDay", lockAtMostFor = "PT30M", lockAtLeastFor = "PT1M")
public void closeDay() {
    ledger.closePending(LocalDate.now(ZoneOffset.UTC).minusDays(1)); // idempotente por fecha
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Una tarea programada con ejecución única entre réplicas, reintentos idempotentes y alerta si no se ejecuta; para volúmenes grandes, un orquestador.
- Registra ejecución, duración y resultado.
### Trampas frecuentes
- Tareas que se ejecutan en cada réplica.
- Reintentos que duplican efectos.
- Sin alerta de tarea no ejecutada.
- Tareas sin límite de tiempo.
- Dependencia de la hora local sin zona.
### Evidencia
- Una alerta salta si la tarea no se ejecuta en su ventana y repetirla no duplica efectos.

## Checklist de revisión
- [ ] Todo `@Scheduled` tiene `@SchedulerLock` o es un CronJob con `Forbid`.
- [ ] Idempotencia y reanudación probadas.
- [ ] Zona horaria explícita; métricas y alerta de "no ejecutado".
- [ ] Chunk size y política skip/retry definidos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep: `@Scheduled` sin `@SchedulerLock` | 1 | `policies/semgrep/java-scheduled-without-lock.yaml` |
| Semgrep: executors sin acotar | 1 | `policies/semgrep/java-unbounded-executors.yaml` |
| Revisión de idempotencia del job | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `scheduling-and-batch`, `batching-and-bulk-ops`, `idempotency-and-deduplication`, `import-export-and-bulk-data`.
- Fuentes: ShedLock README, Spring Batch reference (2026-11-07). Local: Kubernetes local; no se reproduce EventBridge Scheduler de AWS.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
