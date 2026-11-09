---
name: virtual-threads
description: Usar al decidir si usar virtual threads (Java 21+) en Spring Boot o al migrar código bloqueante; cubre pinning, ThreadLocal y límites.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Virtual threads

## Cuándo aplicar y cuándo no
- Aplica a servicios con mucha I/O bloqueante (HTTP, JDBC) con un hilo por petición.
- No aplica a trabajo CPU-bound (no aceleran) ni a código que depende de pools para limitar un recurso escaso sin otro límite.

## Reglas
- **MUST** exigir Java 21+ (virtual threads definitivos, JEP 444). En Spring Boot, activar con `spring.threads.virtual.enabled=true` (Boot 3.2+; verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08).
- **MUST NOT** hacer pool de virtual threads: crear uno por tarea (`Executors.newVirtualThreadPerTaskExecutor()`).
- **MUST** limitar el recurso, no los hilos: usar `Semaphore`, pool de conexiones o bulkhead (ver `backpressure-and-bulkheads`).
- **MUST** vigilar el *pinning*: en Java 21–23 un hilo virtual dentro de `synchronized` con I/O bloqueante fija el hilo portador; preferir `ReentrantLock` en ese código. Java 24 lo mitiga (JEP 491).
- **MUST NOT** almacenar objetos pesados en `ThreadLocal`: hay millones de hilos potenciales. Preferir `ScopedValue` (ver `structured-concurrency-and-scoped-values`).
- **SHOULD** medir con `-Djdk.tracePinnedThreads=full` o eventos JFR `jdk.VirtualThreadPinned` antes de generalizar.
- **SHOULD** medir antes/después (latencia p99, throughput); no asumir mejora.
- **MUST NOT** mezclar con `parallelStream` ni `ForkJoinPool` para I/O.

## Por qué
Un hilo virtual cuesta bytes, no ~1 MB de pila, así que el modelo "un hilo por petición" escala sin reactivo. Pero el cuello de botella pasa a ser el recurso aguas abajo (pool JDBC de 10 conexiones): sin límite explícito, 10 000 hilos virtuales bloquean esperando conexión.

## Ejemplos
### Mal
```java
ExecutorService pool = Executors.newFixedThreadPool(200); // "pool de virtuales" mental
synchronized (this) {
    return httpClient.send(req, BodyHandlers.ofString()); // pinning en Java 21
}
```
### Bien
```java
private final Semaphore downstream = new Semaphore(50);
private final ReentrantLock lock = new ReentrantLock();

try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    exec.submit(() -> {
        downstream.acquire();
        try { return client.fetch(id); } finally { downstream.release(); }
    });
}
```
```properties
spring.threads.virtual.enabled=true
```

## Criterios de decisión y trampas
### Cómo decidir
- Hilos virtuales para trabajo con mucha E/S bloqueante y muchas tareas concurrentes; para cálculo intensivo no aportan nada.
- Con hilos virtuales el límite de concurrencia ya no lo da el pool: usa semáforos o límites en el recurso escaso (conexiones, llamadas a un tercero).
### Trampas frecuentes
- Meter un pool de hilos virtuales (no se reutilizan).
- `synchronized` alrededor de E/S bloqueante, que fija el hilo portador en ciertas versiones.
- Variables locales de hilo pesadas, que se multiplican por millones de hilos.
- Creer que el rendimiento mejora sin cambiar los límites de la base de datos o del servicio remoto.
- No medir antes y después.
### Evidencia
- Una prueba de carga con y sin hilos virtuales y los límites de recurso configurados explícitamente.

## Checklist de revisión
- [ ] Versión de Java >= 21 confirmada.
- [ ] Sin pools de virtual threads; un hilo por tarea.
- [ ] Recursos escasos protegidos con semáforo/pool/bulkhead.
- [ ] Sin I/O bloqueante dentro de `synchronized` (Java < 24).
- [ ] `ThreadLocal` revisados.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep: `synchronized` con I/O no es decidible; solo se detecta pool fijo para virtuales | pendiente | `policies/semgrep/` (pendiente) |
| Evidencia de pinning en test de carga (JFR) | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `threads-executors-and-pools`, `structured-concurrency-and-scoped-values`, `connection-pooling`.
- Fuentes: JEP 444 y JEP 491 (openjdk.org/jeps); documentación de Spring Boot sobre virtual threads.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
