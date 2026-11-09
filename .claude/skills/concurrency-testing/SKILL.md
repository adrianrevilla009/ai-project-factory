---
name: concurrency-testing
description: Usar al escribir tests de código concurrente - carreras, deadlocks, idempotencia bajo doble envío; sin sleeps, con latches y Awaitility.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Tests de concurrencia

## Cuándo aplicar y cuándo no
- Aplica a código con estado compartido, locks, colas, idempotencia, jobs y llamadas asíncronas.
- No aplica a lógica puramente secuencial; ahí bastan tests unitarios normales.

## Reglas
- **MUST** que los tests sean deterministas en su resultado: probar invariantes ("se creó un único pago"), no tiempos.
- **MUST NOT** usar `Thread.sleep` para esperar; usar `CountDownLatch`/`CyclicBarrier`/`Phaser` para sincronizar y Awaitility (`await.atMost(...)`) para esperar condiciones.
- **MUST** arrancar los hilos a la vez con un latch de salida para maximizar la contención.
- **MUST** recoger y propagar las excepciones de los hilos de prueba (`Future.get()`); un fallo en otro hilo no falla el test por sí solo.
- **MUST** poner timeout a cada test concurrente (`@Timeout`, JUnit 5) para que un deadlock no cuelgue el pipeline.
- **MUST** repetir el test (`@RepeatedTest`) para aumentar la probabilidad de exponer carreras; un test que pasa una vez no demuestra ausencia de carrera.
- **SHOULD** usar jcstress para código sin locks/memory model y un thread dump automático en timeout.
- **SHOULD** probar idempotencia y exclusión contra Postgres real (Testcontainers), no mocks.
- **MUST NOT** dejar tests "flaky" en cuarentena sin ticket: o se arreglan o se borran.

## Por qué
Las carreras no se ven en un test secuencial, y un `sleep` mide suerte. Con latches y repetición se fuerza la contención y el fallo se vuelve reproducible. Los timeouts evitan que un deadlock bloquee todo CI.

## Ejemplos
### Mal
```java
@Test
void concurrentPay() throws Exception {
    new Thread(() -> service.pay("k1", req)).start();
    new Thread(() -> service.pay("k1", req)).start();
    Thread.sleep(500);                              // suerte
    assertEquals(1, payments.count());
}
```
### Bien
```java
@RepeatedTest(20)
@Timeout(10)
void samePaymentKey_concurrent_createsOnePayment() throws Exception {
    int n = 8;
    var start = new CountDownLatch(1);
    try (var exec = Executors.newFixedThreadPool(n)) {
        List<Future<Payment>> results = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            results.add(exec.submit(() -> { start.await(); return service.pay("key-example-1", req); }));
        }
        start.countDown();
        for (var f : results) f.get();              // propaga excepciones
    }
    assertThat(payments.countByKey("key-example-1")).isEqualTo(1);
}
```
```java
await().atMost(Duration.ofSeconds(5)).untilAsserted(() -> assertThat(outbox.pending()).isZero());
```

## Checklist de revisión
- [ ] Sin `Thread.sleep` para sincronizar.
- [ ] Latch de arranque simultáneo; excepciones propagadas.
- [ ] `@Timeout` y repetición.
- [ ] Verifica invariantes, no tiempos.
- [ ] Contra BD real si el invariante vive en la BD.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep: `Thread.sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Hook `require-green-tests` al parar | 2 | `.claude/hooks/stop/` (pendiente, Oleada 1) |
| Revisión de tests de carrera | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `java-memory-model`, `locks-and-synchronization`, `idempotency-and-deduplication`, `db-testing`.
- Fuentes: documentación de JUnit 5, Awaitility y jcstress (openjdk).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
