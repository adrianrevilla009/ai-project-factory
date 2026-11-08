# Estándares · 02-concurrency

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## async-and-context-propagation

- **MUST** asumir que `ThreadLocal` (SecurityContext, MDC, tenant, transacción) **no** viaja a otro hilo.
- **MUST** activar `@EnableAsync` y definir un `Executor` propio para `@Async`; nunca depender del defecto implícito.
- **MUST** propagar contexto con un `TaskDecorator` o con Micrometer Context Propagation (`ContextSnapshot`/`ContextExecutorService`, comprobar al fijar la versión) en vez de copiar a mano.
- **MUST** propagar la seguridad con `DelegatingSecurityContextExecutor` (o `DelegatingSecurityContextAsyncTaskExecutor`) de Spring Security (comprobar al fijar la versión).
- **MUST** limpiar el contexto al terminar la tarea (`MDC.clear()` en `finally`) para no contaminar tareas posteriores del pool.
- **MUST NOT** pasar entidades JPA gestionadas ni la transacción al hilo asíncrono; pasar ids o DTO. `@Transactional` no cruza hilos.
- **MUST NOT** esperar que `@Async` funcione en auto-invocación (`this.metodo()`) ni en métodos privados: depende del proxy.
- **MUST** que `@Async void` tenga un `AsyncUncaughtExceptionHandler`; mejor devolver `CompletableFuture`.
- **SHOULD** con virtual threads y Java con `ScopedValue` definitivo, preferirlo a `ThreadLocal` (ver `structured-concurrency-and-scoped-values`).

## backpressure-and-bulkheads

- **MUST** acotar toda cola, buffer y pool; ante saturación, rechazar rápido (429/503) en vez de acumular.
- **MUST** aplicar un bulkhead por dependencia (semáforo o pool dedicado) para que una dependencia lenta no consuma todos los hilos.
- **MUST** poner timeout en cada llamada saliente; sin timeout el bulkhead se llena igual.
- **MUST** que los consumidores de mensajes limiten el prefetch/`max.poll.records` y la concurrencia al ritmo que el proceso aguanta.
- **SHOULD** usar Resilience4j `Bulkhead`/`ThreadPoolBulkhead` y `RateLimiter` (comprobar versión y compatibilidad con la de Spring Boot del proyecto).
- **SHOULD** con virtual threads, limitar con `Semaphore` la concurrencia hacia el recurso (ver `virtual-threads`).
- **MUST** definir degradación explícita (respuesta parcial, caché, valor por defecto) cuando el bulkhead rechaza.
- **MUST NOT** reintentar sin límite ni sin *jitter* contra una dependencia saturada (amplifica la caída).
- **SHOULD** medir saturación (cola, rechazos, esperas) y alertar antes del límite.

## completablefuture-patterns

- **MUST** pasar siempre un `Executor` propio a `*Async`; el defecto es `ForkJoinPool.commonPool()`, compartido con todo el proceso.
- **MUST** definir timeout con `orTimeout(...)` o `completeOnTimeout(...)` (Java 9+).
- **MUST** tratar errores: `exceptionally`/`handle`; una excepción no capturada queda silenciosa hasta el `join`.
- **MUST NOT** llamar `get()`/`join()` dentro de una tarea del mismo pool (interbloqueo por agotamiento).
- **MUST** usar `thenCompose` (aplanar) y no `thenApply` que devuelva otro `CompletableFuture`.
- **SHOULD** `allOf(...)` + recoger resultados con `join()` solo cuando todos han terminado; cancelar `cancel(true)` no interrumpe la tarea en `CompletableFuture`, así que hacer la tarea cooperativa.
- **SHOULD** mantener el contexto (seguridad, MDC) explícitamente (ver `async-and-context-propagation`).
- **MUST NOT** exponer `CompletableFuture` en APIs públicas sin necesidad.

## concurrency-testing

- **MUST** que los tests sean deterministas en su resultado: probar invariantes ("se creó un único pago"), no tiempos.
- **MUST NOT** usar `Thread.sleep` para esperar; usar `CountDownLatch`/`CyclicBarrier`/`Phaser` para sincronizar y Awaitility (`await.atMost(...)`) para esperar condiciones.
- **MUST** arrancar los hilos a la vez con un latch de salida para maximizar la contención.
- **MUST** recoger y propagar las excepciones de los hilos de prueba (`Future.get()`); un fallo en otro hilo no falla el test por sí solo.
- **MUST** poner timeout a cada test concurrente (`@Timeout`, JUnit 5) para que un deadlock no cuelgue el pipeline.
- **MUST** repetir el test (`@RepeatedTest`) para aumentar la probabilidad de exponer carreras; un test que pasa una vez no demuestra ausencia de carrera.
- **SHOULD** usar jcstress para código sin locks/memory model (comprobar al fijar la versión) y un thread dump automático en timeout.
- **SHOULD** probar idempotencia y exclusión contra Postgres real (Testcontainers), no mocks.
- **MUST NOT** dejar tests "flaky" en cuarentena sin ticket: o se arreglan o se borran.

## concurrent-collections

- **MUST NOT** compartir `HashMap`, `ArrayList` o `HashSet` entre hilos con escritores.
- **MUST** preferir `ConcurrentHashMap` a `Collections.synchronizedMap` salvo que se necesite bloqueo externo.
- **MUST** usar operaciones atómicas (`computeIfAbsent`, `merge`, `compute`, `putIfAbsent`); **MUST NOT** hacer `if (!map.containsKey(k)) map.put(k, v)`.
- **MUST** que la función pasada a `compute*` sea corta, sin I/O y sin tocar el mismo mapa (puede bloquear o lanzar excepción).
- **SHOULD** usar `CopyOnWriteArrayList` solo con lecturas dominantes y escrituras raras; cada escritura copia el array.
- **MUST** usar colas acotadas (`ArrayBlockingQueue`, `LinkedBlockingQueue(capacity)`) para productor/consumidor; nunca sin cota.
- **MUST NOT** asumir que `size()` o una iteración son instantáneas consistentes; son débilmente consistentes.
- **SHOULD** usar `LongAdder` para contadores con mucha contención.
- **MUST** definir expulsión/tamaño máximo en caches en memoria; preferir Caffeine a un mapa propio.

## distributed-locking

- **MUST** agotar primero alternativas sin lock: `UNIQUE`, versión optimista (`optimistic-locking`), `SELECT ... FOR UPDATE SKIP LOCKED`, cola particionada.
- **MUST** que todo lock tenga TTL/lease; un lock sin expiración deja el sistema bloqueado si el titular muere.
- **MUST** asumir que el titular puede perder el lock sin saberlo (pausa GC, partición): proteger el recurso con un *fencing token* monotónico que el recurso verifique, o hacer la operación idempotente.
- **MUST NOT** usar un lock distribuido como única garantía de corrección de dinero o inventario.
- **MUST** liberar solo si se es titular (valor único por adquisición, comparar-y-borrar atómico).
- **SHOULD** usar el almacén que el proyecto ya tiene y respeta D16 (sin licencias de pago): Postgres (`pg_advisory_xact_lock` o tabla con lease) o ShedLock (Apache-2.0, comprobar al fijar la versión) sobre JDBC para jobs.
- **MUST NOT** tomar un lock Redis de una sola instancia como si fuera consenso; Redlock es controvertido (comprobar al fijar la versión) y no sustituye al fencing.
- **SHOULD** acotar la sección crítica a bastante menos que el TTL y exponer métricas de adquisición/espera.
- En local se usa el mismo mecanismo sobre el Postgres de desarrollo; no se reproducen fallos de red/partición realistas de AWS.

## idempotency-and-deduplication

- **MUST** asumir entrega *at-least-once*: todo consumidor y todo endpoint con reintento debe tolerar duplicados.
- **MUST** exigir en `POST` con efecto una clave de cliente (cabecera `Idempotency-Key`; el estándar IETF sigue siendo un borrador, `draft-ietf-httpapi-idempotency-key-header-08`, ya en la cola del RFC Editor; verificado el 2026-11-08) y guardarla con el resultado.
- **MUST** hacer la reserva de la clave atómica con una restricción `UNIQUE` en la misma transacción que el efecto; no "consultar y luego insertar".
- **MUST** que la misma clave con cuerpo distinto devuelva error (422/409), y con el mismo cuerpo devuelva la respuesta original.
- **MUST** deduplicar mensajes por id de evento (tabla `processed_message` con `UNIQUE(message_id, consumer)`) en la misma transacción que el efecto.
- **MUST** definir retención/TTL de las claves y limpiarlas.
- **MUST NOT** deduplicar solo en memoria ni en caché volátil.
- **MUST NOT** implementar doble escritura Postgres+NoSQL para guardar las claves; una sola fuente de verdad.
- **SHOULD** combinar con *outbox* para publicar eventos de forma exactamente-una-vez-efectiva.

## java-memory-model

- **MUST** que toda escritura compartida tenga una relación *happens-before* con la lectura: `synchronized`, `volatile`, `Lock`, `final`, estructuras concurrentes o `Thread.start/join`.
- **MUST** declarar `volatile` los flags de estado simples (parada, "ready") leídos por otros hilos.
- **MUST NOT** usar `volatile` para operaciones compuestas (`count++`, check-then-act); usar `AtomicInteger`/`LongAdder` o un lock.
- **MUST** publicar objetos de forma segura: campo `final`, `volatile`, dentro de un lock o vía `ConcurrentHashMap`/`BlockingQueue`.
- **MUST** preferir objetos inmutables (campos `final`, records, colecciones `List.copyOf`); son seguros sin sincronización.
- **MUST NOT** hacer double-checked locking sin `volatile`; preferir holder idiom o `enum`.
- **MUST NOT** dejar escapar `this` desde el constructor (registrar listeners, arrancar hilos).
- **SHOULD** tratar `long`/`double` no volátiles como no atómicos.
- **SHOULD** validar código sin locks con herramientas (jcstress), no con "funciona en mi máquina".

## locks-and-synchronization

- **MUST** mantener la sección crítica mínima y sin I/O, llamadas remotas ni código ajeno (callbacks) dentro.
- **MUST** liberar `Lock` en `finally`; usar `tryLock(timeout)` cuando haya riesgo de espera larga.
- **MUST** fijar un orden global al adquirir varios locks (p. ej. por id ascendente) para evitar deadlocks.
- **MUST NOT** sincronizar sobre `this`, `String`, enteros "boxed" ni objetos públicos; usar un `private final Object lock`.
- **MUST NOT** llamar a métodos *alien* (sobrescribibles, listeners) con un lock tomado.
- **SHOULD** preferir `AtomicReference`/`LongAdder`/`ConcurrentHashMap.compute` antes que un lock manual.
- **SHOULD** usar `ReentrantLock` en vez de `synchronized` si se bloquea con I/O bajo virtual threads en Java < 24 (ver `virtual-threads`).
- **SHOULD** usar `StampedLock`/`ReadWriteLock` solo con evidencia de lecturas dominantes; son más difíciles de usar bien.
- **MUST** documentar con `@GuardedBy` (o comentario) qué lock protege cada campo.

## scheduling-and-batch

- **MUST** asumir varias instancias: todo `@Scheduled` en un servicio con más de una réplica necesita ejecución única (ShedLock, comprobar al fijar la versión; o un `CronJob` de Kubernetes fuera del servicio).
- **MUST** que el job sea idempotente y reanudable: procesa por lotes con marca de progreso; relanzarlo no duplica efectos (ver `idempotency-and-deduplication`).
- **MUST** configurar el scheduler de Spring con pool propio: por defecto `@Scheduled` usa un solo hilo y un job lento bloquea a los demás (`spring.task.scheduling.pool.size`, comprobar al fijar la versión).
- **MUST** capturar y registrar excepciones; un job que falla en silencio no se repara.
- **MUST** fijar zona horaria explícita en cron (`zone = "UTC"` o la de negocio).
- **MUST** procesar en trozos (chunks) con transacción por trozo; **MUST NOT** cargar todo el conjunto en memoria (ver `pagination`, `batching-and-bulk-ops`).
- **SHOULD** usar Spring Batch cuando se necesite reinicio, saltos (`skip`), reintentos y metadatos de ejecución.
- **SHOULD** emitir métricas (duración, procesados, fallos) y alertar si un job no corre.
- **MUST NOT** ejecutar `@Scheduled` con `fixedRate` si la ejecución puede solaparse; usar `fixedDelay`.

## structured-concurrency-and-scoped-values

- **MUST** comprobar el estado del JEP en la versión de JDK del proyecto: `StructuredTaskScope` ha sido API en preview en varias versiones y su forma ha cambiado; `ScopedValue` pasó a definitivo más tarde (comprobar JEP 505/506 y versión de JDK).
- **MUST NOT** usar APIs en preview en código de producción sin decisión explícita (ADR) y `--enable-preview` documentado en el build.
- **MUST** si no hay preview: lograr el mismo efecto con `ExecutorService` + `close()` en try-with-resources, y cancelar hermanas ante fallo.
- **MUST** que el ámbito de la tarea cierre antes que el método que la abrió (try-with-resources); nada de subtareas que sobrevivan al llamante.
- **MUST** definir política de fallo: "todas o ninguna" (cancelar al primer error) o "la primera que acabe".
- **SHOULD** preferir `ScopedValue` a `ThreadLocal` para contexto inmutable; es heredado por subtareas del ámbito estructurado.
- **MUST NOT** mutar un `ScopedValue`; se rebindea con `ScopedValue.where(...).run(...)`.
- **SHOULD** poner timeout global del ámbito.

## threads-executors-and-pools

- **MUST** crear pools con `ThreadPoolExecutor` (o `ThreadPoolTaskExecutor`) con cola **acotada**, tamaño máximo explícito y política de rechazo definida.
- **MUST NOT** usar `Executors.newCachedThreadPool()` (hilos ilimitados) ni `newFixedThreadPool()` en producción (cola `LinkedBlockingQueue` sin límite).
- **MUST NOT** usar `new Thread(...)` para trabajo de negocio.
- **MUST** dar nombre a los hilos (`ThreadFactory` o `threadNamePrefix`) para poder leer thread dumps y logs.
- **MUST** separar pools por tipo de trabajo (CPU vs I/O bloqueante vs recurso externo) para que uno no agote a otro.
- **MUST** cerrar los executors en el ciclo de vida (`@PreDestroy`, bean con `destroyMethod`, `close()` en Java 19+) y esperar la terminación con timeout.
- **SHOULD** dimensionar CPU-bound con ~nº de núcleos y I/O-bound con la fórmula `núcleos * (1 + espera/cómputo)`, medida y no supuesta.
- **SHOULD** exponer métricas del pool (activos, cola, rechazos) vía Micrometer.
- **MUST NOT** usar `parallelStream()` sobre I/O ni en peticiones web (comparte el `ForkJoinPool.commonPool`).

## virtual-threads

- **MUST** exigir Java 21+ (virtual threads definitivos, JEP 444). En Spring Boot, activar con `spring.threads.virtual.enabled=true` (comprobar versión mínima de Boot).
- **MUST NOT** hacer pool de virtual threads: crear uno por tarea (`Executors.newVirtualThreadPerTaskExecutor()`).
- **MUST** limitar el recurso, no los hilos: usar `Semaphore`, pool de conexiones o bulkhead (ver `backpressure-and-bulkheads`).
- **MUST** vigilar el *pinning*: en Java 21–23 un hilo virtual dentro de `synchronized` con I/O bloqueante fija el hilo portador; preferir `ReentrantLock` en ese código. Java 24 lo mitiga (JEP 491, comprobar al fijar la versión).
- **MUST NOT** almacenar objetos pesados en `ThreadLocal`: hay millones de hilos potenciales. Preferir `ScopedValue` (ver `structured-concurrency-and-scoped-values`).
- **SHOULD** medir con `-Djdk.tracePinnedThreads=full` o eventos JFR `jdk.VirtualThreadPinned` antes de generalizar.
- **SHOULD** medir antes/después (latencia p99, throughput); no asumir mejora.
- **MUST NOT** mezclar con `parallelStream` ni `ForkJoinPool` para I/O.
