---
name: completablefuture-patterns
description: Usar al componer tareas asíncronas con CompletableFuture - executor explícito, timeouts, manejo de errores y combinación.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Patrones con CompletableFuture

## Cuándo aplicar y cuándo no
- Aplica al usar `supplyAsync`, `thenCompose`, `allOf`, etc. en servicios.
- No aplica a código con virtual threads donde basta código secuencial bloqueante (ver `virtual-threads`), ni a pipelines reactivos.

## Reglas
- **MUST** pasar siempre un `Executor` propio a `*Async`; el defecto es `ForkJoinPool.commonPool()`, compartido con todo el proceso.
- **MUST** definir timeout con `orTimeout(...)` o `completeOnTimeout(...)` (Java 9+).
- **MUST** tratar errores: `exceptionally`/`handle`; una excepción no capturada queda silenciosa hasta el `join`.
- **MUST NOT** llamar `get()`/`join()` dentro de una tarea del mismo pool (interbloqueo por agotamiento).
- **MUST** usar `thenCompose` (aplanar) y no `thenApply` que devuelva otro `CompletableFuture`.
- **SHOULD** `allOf(...)` + recoger resultados con `join()` solo cuando todos han terminado; cancelar `cancel(true)` no interrumpe la tarea en `CompletableFuture`, así que hacer la tarea cooperativa.
- **SHOULD** mantener el contexto (seguridad, MDC) explícitamente (ver `async-and-context-propagation`).
- **MUST NOT** exponer `CompletableFuture` en APIs públicas sin necesidad.

## Por qué
`supplyAsync(fn)` sin executor mete I/O bloqueante en el pool común y puede paralizar `parallelStream` y otras librerías. Sin timeout, una dependencia lenta retiene recursos indefinidamente. `cancel` solo completa el futuro, no detiene el hilo.

## Ejemplos
### Mal
```java
CompletableFuture<Price> p = CompletableFuture.supplyAsync(() -> pricing.fetch(id));
return p.get(); // sin executor, sin timeout, sin manejo de error
```
### Bien
```java
CompletableFuture<Price> price = CompletableFuture
    .supplyAsync(() -> pricing.fetch(id), ioExecutor)
    .orTimeout(2, TimeUnit.SECONDS)
    .exceptionally(ex -> Price.unavailable(id));

CompletableFuture<Stock> stock = CompletableFuture
    .supplyAsync(() -> stockClient.get(id), ioExecutor)
    .orTimeout(2, TimeUnit.SECONDS);

return price.thenCombine(stock, Offer::new).join();
```

## Checklist de revisión
- [ ] Todo `*Async` lleva executor propio.
- [ ] Timeout en cada llamada externa.
- [ ] Errores tratados; no hay `join` en el mismo pool.
- [ ] `thenCompose` donde corresponde.
- [ ] Contexto propagado si hace falta.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep: `supplyAsync`/`runAsync` con un solo argumento | 1 | `policies/semgrep/java-completablefuture-default-pool.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Revisión de timeouts y errores | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `threads-executors-and-pools`, `async-and-context-propagation`, `backpressure-and-bulkheads`.
- Fuentes: Javadoc de `java.util.concurrent.CompletableFuture`.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
