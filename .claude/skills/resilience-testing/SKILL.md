---
name: resilience-testing
description: "Usar al escribir tests automáticos que comprueban timeouts, retries, circuit breaker, bulkheads y degradación ante fallos de dependencias."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Tests de resiliencia

## Cuándo aplicar y cuándo no
- Aplica a todo cliente de dependencia externa (HTTP, BD, broker) con políticas de timeout, retry, circuit breaker o fallback.
- No aplica a experimentos exploratorios en entornos compartidos: eso es `chaos-engineering`. Aquí los fallos se simulan de forma determinista en el pipeline.

## Reglas
- **MUST** tener un test por cada política de resiliencia declarada: timeout, número de reintentos, apertura y cierre del breaker, fallback.
- **MUST** simular el fallo de forma determinista: WireMock (`withFixedDelay`, `Fault`), Toxiproxy en Testcontainers (latencia, corte), o dobles que lanzan excepciones.
- **MUST** verificar el resultado observable: respuesta degradada correcta, código de error esperado, métricas del breaker, ausencia de efectos duplicados.
- **MUST** comprobar que los reintentos son idempotentes (ver `idempotency-keys`) y con backoff y jitter acotados.
- **MUST NOT** usar `Thread.sleep` para esperar el estado del breaker; usar Awaitility o reloj controlable.
- **MUST NOT** probar la política con timeouts reales largos: configurarlos pequeños en el perfil de test.
- **SHOULD** probar la recuperación (la dependencia vuelve y el breaker cierra).
- **SHOULD** cubrir apagado ordenado y reinicio de dependencia (ver `graceful-shutdown-lifecycle`).

## Por qué
Las políticas de resiliencia son código con ramas que casi nunca se ejecutan en condiciones normales; sin tests, el primer uso real ocurre en un incidente. Los fallos deterministas hacen el test estable.

## Ejemplos
### Mal
```java
@Test
void callsPayment() {
    assertThat(client.charge(order)).isNotNull(); // solo camino feliz
}
```
### Bien
```java
@Test
void timesOutAndFallsBackWhenPaymentIsSlow(WireMockRuntimeInfo wm) {
    stubFor(post("/charge").willReturn(ok().withFixedDelay(3_000))); // timeout de test: 500 ms

    var result = client.charge(order);

    assertThat(result.status()).isEqualTo(ChargeStatus.PENDING_RETRY);
    verify(1, postRequestedFor(urlEqualTo("/charge")));
}

@Test
void opensCircuitAfterRepeatedFailures() {
    stubFor(post("/charge").willReturn(serverError()));
    repeat(10, () -> client.charge(order));

    await().atMost(Duration.ofSeconds(2)).untilAsserted(() ->
        assertThat(circuitBreakerRegistry.circuitBreaker("payment").getState())
            .isEqualTo(CircuitBreaker.State.OPEN));
}
```
Clases de Resilience4j y WireMock: comprobar contra la versión usada.

## Checklist de revisión
- [ ] Un test por política declarada (timeout, retry, breaker, fallback).
- [ ] Fallos simulados de forma determinista, sin sleeps.
- [ ] Verificada la idempotencia de reintentos.
- [ ] Probada la recuperación tras el fallo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: cliente HTTP sin timeout | 1 | `policies/semgrep/spring-http-client-without-timeout.yaml` |
| Regla Semgrep: `Thread.sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` |
| Hook que exige tests en verde al parar | 2 | `.claude/hooks/stop/require_green_tests.py` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `resilience`, `chaos-engineering`, `wiremock-and-stubbing`, `http-clients-and-timeouts`, `backpressure-and-bulkheads`.
- Fuentes: documentación de Resilience4j (https://resilience4j.readme.io/) y WireMock (https://wiremock.org/docs/), comprobar API a 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
