---
name: threads-executors-and-pools
description: Usar al crear hilos, ExecutorService, pools o @Async en Java/Spring; define dimensionado, colas acotadas, nombres de hilo y cierre.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Hilos, executors y pools

## Cuándo aplicar y cuándo no
- Aplica a cualquier `new Thread`, `Executors.*`, `ThreadPoolTaskExecutor`, `@Async` o `parallelStream()` en código de servicio.
- No aplica a código que ya delega en virtual threads (ver `virtual-threads`) salvo para pools de recursos limitados.

## Reglas
- **MUST** crear pools con `ThreadPoolExecutor` (o `ThreadPoolTaskExecutor`) con cola **acotada**, tamaño máximo explícito y política de rechazo definida.
- **MUST NOT** usar `Executors.newCachedThreadPool()` (hilos ilimitados) ni `newFixedThreadPool()` en producción (cola `LinkedBlockingQueue` sin límite).
- **MUST NOT** usar `new Thread(...)` para trabajo de negocio.
- **MUST** dar nombre a los hilos (`ThreadFactory` o `threadNamePrefix`) para poder leer thread dumps y logs.
- **MUST** separar pools por tipo de trabajo (CPU vs I/O bloqueante vs recurso externo) para que uno no agote a otro.
- **MUST** cerrar los executors en el ciclo de vida (`@PreDestroy`, bean con `destroyMethod`, `close()` en Java 19+) y esperar la terminación con timeout.
- **SHOULD** dimensionar CPU-bound con ~nº de núcleos y I/O-bound con la fórmula `núcleos * (1 + espera/cómputo)`, medida y no supuesta.
- **SHOULD** exponer métricas del pool (activos, cola, rechazos) vía Micrometer.
- **MUST NOT** usar `parallelStream()` sobre I/O ni en peticiones web (comparte el `ForkJoinPool.commonPool`).

## Por qué
Un pool sin cota convierte un pico de carga en OOM (cola infinita) o en miles de hilos (cached). Una cola acotada con rechazo explícito traslada la presión hacia atrás (ver `backpressure-and-bulkheads`). Los hilos anónimos (`pool-3-thread-7`) hacen inútil un thread dump.

## Ejemplos
### Mal
```java
ExecutorService pool = Executors.newFixedThreadPool(8); // cola ilimitada
pool.submit(() -> sendEmail(order));                    // sin nombre, sin cierre
```
### Bien
```java
@Bean(destroyMethod = "shutdown")
ThreadPoolTaskExecutor emailExecutor() {
    var ex = new ThreadPoolTaskExecutor();
    ex.setThreadNamePrefix("email-");
    ex.setCorePoolSize(4);
    ex.setMaxPoolSize(8);
    ex.setQueueCapacity(200);
    ex.setRejectedExecutionHandler(new ThreadPoolExecutor.CallerRunsPolicy());
    ex.setWaitForTasksToCompleteOnShutdown(true);
    ex.setAwaitTerminationSeconds(30);
    return ex;
}
```
`CallerRunsPolicy` frena al productor; si el productor es un hilo de petición, valorar `AbortPolicy` y responder 503.

## Checklist de revisión
- [ ] Ningún `new Thread` ni `Executors.newCachedThreadPool/newFixedThreadPool`.
- [ ] Cola acotada y política de rechazo elegida a propósito.
- [ ] Hilos con nombre; pool con métricas.
- [ ] Cierre ordenado con timeout.
- [ ] Pools separados por tipo de carga.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep contra `new Thread` y executors sin cota | 1 | `policies/semgrep/java-unbounded-executors.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Revisión de dimensionado | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `virtual-threads`, `backpressure-and-bulkheads`, `async-and-context-propagation`.
- Fuentes: Javadoc de `java.util.concurrent.ThreadPoolExecutor` y referencia de Spring `TaskExecutor`.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
