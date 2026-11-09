---
name: scheduling-and-batch
description: Usar al crear tareas @Scheduled, jobs periódicos o procesos batch (Spring Batch); ejecución única en clúster, idempotencia y reanudación.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Scheduling y batch

## Cuándo aplicar y cuándo no
- Aplica a `@Scheduled`, cron, jobs de reconciliación/limpieza y procesos de volumen (Spring Batch).
- No aplica a flujos disparados por eventos o peticiones; ni a orquestación de larga vida con estado (ver `sagas-and-process-managers`).

## Reglas
- **MUST** asumir varias instancias: todo `@Scheduled` en un servicio con más de una réplica necesita ejecución única (ShedLock; o un `CronJob` de Kubernetes fuera del servicio).
- **MUST** que el job sea idempotente y reanudable: procesa por lotes con marca de progreso; relanzarlo no duplica efectos (ver `idempotency-and-deduplication`).
- **MUST** configurar el scheduler de Spring con pool propio: por defecto `@Scheduled` usa un solo hilo y un job lento bloquea a los demás (`spring.task.scheduling.pool.size`, verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08).
- **MUST** capturar y registrar excepciones; un job que falla en silencio no se repara.
- **MUST** fijar zona horaria explícita en cron (`zone = "UTC"` o la de negocio).
- **MUST** procesar en trozos (chunks) con transacción por trozo; **MUST NOT** cargar todo el conjunto en memoria (ver `pagination`, `batching-and-bulk-ops`).
- **SHOULD** usar Spring Batch cuando se necesite reinicio, saltos (`skip`), reintentos y metadatos de ejecución.
- **SHOULD** emitir métricas (duración, procesados, fallos) y alertar si un job no corre.
- **MUST NOT** ejecutar `@Scheduled` con `fixedRate` si la ejecución puede solaparse; usar `fixedDelay`.

## Por qué
Con 3 réplicas, un cron sin lock se ejecuta 3 veces: tres cierres de caja, tres emails. Y un job que se reinicia a mitad sin marca de progreso reprocesa todo o se deja a medias.

## Ejemplos
### Mal
```java
@Scheduled(cron = "0 0 * * * *")
public void sendReminders() {
    userRepository.findAll().forEach(mailer::send);  // N réplicas = N envíos; todo en memoria
}
```
### Bien
```java
@Scheduled(cron = "0 0 * * * *", zone = "UTC")
@SchedulerLock(name = "sendReminders", lockAtMostFor = "PT10M", lockAtLeastFor = "PT30S")
public void sendReminders() {
    List<Reminder> batch;
    while (!(batch = reminders.nextPendingBatch(500)).isEmpty()) { // marca de progreso en BD
        batch.forEach(r -> mailer.sendOnce(r.id(), r));            // idempotente por id
        reminders.markSent(batch);
    }
}
```

## Checklist de revisión
- [ ] Ejecución única en clúster resuelta.
- [ ] Job idempotente, por lotes y reanudable.
- [ ] Pool de scheduler y zona horaria definidos.
- [ ] Errores registrados y métricas expuestas.
- [ ] Sin `fixedRate` solapable.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep: `@Scheduled` sin `@SchedulerLock` | 1 | `policies/semgrep/java-scheduled-without-lock.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Revisión de idempotencia del job | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `distributed-locking`, `idempotency-and-deduplication`, `batching-and-bulk-ops`, `graceful-shutdown-lifecycle`.
- Fuentes: documentación de Spring (Task Execution and Scheduling), Spring Batch y ShedLock.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
