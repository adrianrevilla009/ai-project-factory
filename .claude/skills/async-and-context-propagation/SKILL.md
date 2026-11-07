---
name: async-and-context-propagation
description: Usar con @Async, executors y CompletableFuture cuando deban conservar seguridad, MDC, trace id o tenant; propagación de contexto entre hilos.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# @Async y propagación de contexto

## Cuándo aplicar y cuándo no
- Aplica a cualquier trabajo que cambie de hilo y necesite `SecurityContext`, MDC (logs), traza distribuida o tenant.
- No aplica a código síncrono en el hilo de la petición.

## Reglas
- **MUST** asumir que `ThreadLocal` (SecurityContext, MDC, tenant, transacción) **no** viaja a otro hilo.
- **MUST** activar `@EnableAsync` y definir un `Executor` propio para `@Async`; nunca depender del defecto implícito.
- **MUST** propagar contexto con un `TaskDecorator` o con Micrometer Context Propagation (`ContextSnapshot`/`ContextExecutorService`, TODO-VERIFY) en vez de copiar a mano.
- **MUST** propagar la seguridad con `DelegatingSecurityContextExecutor` (o `DelegatingSecurityContextAsyncTaskExecutor`) de Spring Security (TODO-VERIFY).
- **MUST** limpiar el contexto al terminar la tarea (`MDC.clear()` en `finally`) para no contaminar tareas posteriores del pool.
- **MUST NOT** pasar entidades JPA gestionadas ni la transacción al hilo asíncrono; pasar ids o DTO. `@Transactional` no cruza hilos.
- **MUST NOT** esperar que `@Async` funcione en auto-invocación (`this.metodo()`) ni en métodos privados: depende del proxy.
- **MUST** que `@Async void` tenga un `AsyncUncaughtExceptionHandler`; mejor devolver `CompletableFuture`.
- **SHOULD** con virtual threads y Java con `ScopedValue` definitivo, preferirlo a `ThreadLocal` (ver `structured-concurrency-and-scoped-values`).

## Por qué
El síntoma típico: logs sin trace id desde el hilo asíncrono, autorizaciones que fallan con `anonymous` o, peor, datos de otro tenant visibles porque el hilo del pool conservó un contexto anterior. Los fallos son intermitentes y aparecen bajo carga.

## Ejemplos
### Mal
```java
@Async
public void notifyCustomer(Long orderId) {
    log.info("notifying");                       // sin traceId en MDC
    var user = SecurityContextHolder.getContext().getAuthentication(); // null
}
```
### Bien
```java
@Configuration
@EnableAsync
class AsyncConfig {
    @Bean(name = "appTaskExecutor")
    ThreadPoolTaskExecutor appTaskExecutor() {
        var ex = new ThreadPoolTaskExecutor();
        ex.setThreadNamePrefix("async-");
        ex.setCorePoolSize(4); ex.setMaxPoolSize(8); ex.setQueueCapacity(100);
        ex.setTaskDecorator(task -> {
            var mdc = MDC.getCopyOfContextMap();
            return () -> {
                try { if (mdc != null) MDC.setContextMap(mdc); task.run(); }
                finally { MDC.clear(); }
            };
        });
        return ex;
    }
}

@Async("appTaskExecutor")
public CompletableFuture<Void> notifyCustomer(Long orderId) { /* carga por id */ }
```

## Checklist de revisión
- [ ] Executor propio para `@Async`, con `@EnableAsync`.
- [ ] MDC, seguridad y tenant propagados y limpiados.
- [ ] No se pasan entidades gestionadas; no se espera transacción.
- [ ] Sin auto-invocación de métodos `@Async`.
- [ ] Manejo de excepciones asíncronas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Test de integración que verifica traceId/seguridad en hilo asíncrono | pendiente | tests del proyecto generado |
| Revisión de uso de `@Async` | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `threads-executors-and-pools`, `completablefuture-patterns`, `multi-tenancy`, `logging-rules`.
- Fuentes: referencia de Spring Framework (`@Async`, `TaskDecorator`), Spring Security (concurrency) y Micrometer Context Propagation — TODO-VERIFY URLs (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
