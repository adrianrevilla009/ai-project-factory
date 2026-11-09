---
name: resilience
description: Usar al proteger llamadas a dependencias externas con Resilience4j (circuit breaker, retry, bulkhead, time limiter, rate limiter) en servicios Spring Boot.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Resiliencia con Resilience4j

## Cuándo aplicar y cuándo no
- Aplica a llamadas síncronas a servicios remotos, APIs de terceros y recursos compartidos con riesgo de saturación.
- No aplica a lógica local pura ni a operaciones dentro de una transacción de base de datos propia (usar timeouts de la transacción).

## Reglas
- **MUST** poner un timeout de cliente (`http-clients-and-timeouts`) antes de añadir cualquier patrón; resiliencia sin timeout no protege.
- **MUST** reintentar solo operaciones idempotentes o con clave de idempotencia, con backoff exponencial y jitter, y número máximo bajo (2-3).
- **MUST** definir `fallback` explícito y de significado de negocio claro, o dejar propagar el error; **MUST NOT** devolver listas vacías o `null` que oculten el fallo.
- **MUST** configurar instancias por nombre en `application.yml`, una por dependencia, no valores en anotaciones.
- **MUST** usar `Bulkhead` (semáforo) para limitar concurrencia hacia dependencias lentas.
- **SHOULD** orden de composición documentado: Retry envuelve a CircuitBreaker, que envuelve a TimeLimiter/Bulkhead.
- **SHOULD** exponer métricas y estado de los breakers vía Actuator (`actuator-and-health`).
- **MUST NOT** hacer retry anidado en varias capas (multiplica la carga: 3x3x3).

## Por qué
Los fallos parciales se amplifican: reintentos sin control convierten una lentitud en una caída (tormenta de reintentos). El circuit breaker corta la carga hacia lo que ya falla y da tiempo a recuperarse. Los umbrales concretos dependen de cada dependencia y deben medirse, no copiarse.

## Ejemplos
### Mal
```java
@Retry(name = "default", fallbackMethod = "empty")   // retry sobre POST no idempotente
public Receipt charge(ChargeRequest req) { return client.charge(req); }

private Receipt empty(ChargeRequest req, Exception e) { return null; } // oculta el fallo
```
### Bien
```java
@CircuitBreaker(name = "payments", fallbackMethod = "chargeUnavailable")
public Receipt charge(ChargeRequest req, String idempotencyKey) {
    return client.charge(req, idempotencyKey);
}

private Receipt chargeUnavailable(ChargeRequest req, String key, CallNotPermittedException e) {
    throw new PaymentTemporarilyUnavailableException(e);   // -> 503 con Problem Details
}
```
```yaml
resilience4j:
  circuitbreaker:
    instances:
      payments:
        sliding-window-size: 20
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
  retry:
    instances:
      payments:
        max-attempts: 3
        wait-duration: 200ms
        enable-exponential-backoff: true
```
Los valores son ilustrativos; calibrar con métricas reales. Nombres de propiedades.

## Checklist de revisión
- [ ] Hay timeout antes que retry/breaker.
- [ ] Retry solo sobre operaciones idempotentes, con backoff y tope.
- [ ] Fallback con significado de negocio o error propagado.
- [ ] Un solo nivel de retry en la cadena de llamadas.
- [ ] Métricas del breaker visibles en Actuator.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de llamadas remotas nuevas | 3 | agente `code-reviewer` |
| Test de fallo/timeout con WireMock (bloque 08) | 1 | tests del proyecto generado (pendiente) |
| Regla Semgrep: `@Retry` en métodos POST | 1 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `http-clients-and-timeouts`, `actuator-and-health`, `idempotency-keys`, `resilience-testing`.
- Fuentes: documentación oficial de Resilience4j y de Spring Cloud Circuit Breaker.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
