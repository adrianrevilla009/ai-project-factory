---
name: exceptions-and-error-handling
description: Usar al lanzar, capturar, envolver o registrar excepciones en Java; define jerarquía de dominio, causa original y límites donde se traducen.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Excepciones y gestión de errores

## Cuándo aplicar y cuándo no
- Aplica a cualquier `try/catch`, `throw`, clase de excepción nueva y conversión de errores en bordes (HTTP, mensajería, JDBC).
- No aplica al formato de respuesta HTTP de error (ver `error-handling-problem-details`).

## Reglas
- **MUST** lanzar excepciones específicas de dominio (`InsufficientStockException`) que extiendan `RuntimeException`; reservar checked exceptions para fallos recuperables que el llamante pueda tratar de forma distinta.
- **MUST** preservar la causa: `new DomainException("msg", e)`.
- **MUST NOT** capturar `Throwable` ni `Error`; **MUST NOT** capturar `Exception` salvo en un límite de proceso (consumidor de cola, handler global).
- **MUST NOT** tragar excepciones con `catch` vacío; si se ignora a propósito, comentar el motivo y registrar a nivel DEBUG.
- **MUST NOT** registrar y relanzar la misma excepción en cada capa (duplica el log): se registra una sola vez, en el límite que la gestiona.
- **MUST** usar try-with-resources para todo `AutoCloseable`.
- **MUST NOT** usar excepciones para control de flujo normal.
- **MUST NOT** incluir secretos o datos personales en el mensaje de la excepción.
- **SHOULD** validar argumentos con `IllegalArgumentException`/`IllegalStateException` y mensajes que incluyan el valor ofensor no sensible.
- **MUST** restaurar el flag de interrupción tras capturar `InterruptedException` (`Thread.currentThread().interrupt()`).

## Por qué
Perder la causa convierte un incidente en una búsqueda a ciegas. Capturar `Exception` genérica oculta fallos de programación (NPE) como errores de negocio. Un log por capa crea ruido y falsos positivos de alertas. Tragar `InterruptedException` impide el apagado ordenado.

## Ejemplos
### Mal
```java
try {
    gateway.charge(order);
} catch (Exception e) {
    log.error("failed " + e.getMessage());
    throw new RuntimeException("payment failed");   // causa perdida, doble log
}
```
### Bien
```java
try {
    gateway.charge(order);
} catch (GatewayTimeoutException e) {
    throw new PaymentUnavailableException("charge timed out for order " + order.id(), e);
}

try (var in = Files.newInputStream(path)) {
    return parser.parse(in);
} catch (IOException e) {
    throw new UncheckedIOException("cannot read " + path.getFileName(), e);
}
```

## Checklist de revisión
- [ ] Cada `catch` es específico y conserva la causa.
- [ ] No hay `catch` vacíos ni de `Throwable`.
- [ ] El error se registra una sola vez, en el límite.
- [ ] Recursos en try-with-resources; interrupciones restauradas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep `java-catch-throwable-or-swallow` | 1 | `policies/semgrep/java-language-pitfalls.yaml` |
| Revisión de jerarquía y límites de captura | 3 | agente `code-reviewer` (pendiente de definir) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `logging-rules`, `null-safety`, `error-handling-problem-details`, `locks-and-synchronization`.
- Fuentes: Effective Java (Bloch), capítulo de excepciones (libro); Javadoc `java.lang.Thread#interrupt` — no verificado en línea.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
