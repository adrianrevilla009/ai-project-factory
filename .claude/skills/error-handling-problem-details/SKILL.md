---
name: error-handling-problem-details
description: "Usar al diseñar el manejo de errores HTTP en Spring: ProblemDetail (RFC 9457), @RestControllerAdvice y sin filtrar trazas."
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Errores HTTP con Problem Details (RFC 9457)

## Cuándo aplicar y cuándo no
- Aplica a toda API REST Spring MVC que devuelva errores al cliente.
- No aplica a errores de mensajería (ver `dlq-retries-poison-messages`) ni a páginas de error HTML.

## Reglas
- **MUST** responder errores con `application/problem+json` usando `ProblemDetail` de Spring (RFC 9457, que sustituye a RFC 7807).
- **MUST** centralizar el mapeo en un único `@RestControllerAdvice`, preferiblemente extendiendo `ResponseEntityExceptionHandler`.
- **MUST** incluir `type` (URI estable por tipo de error), `title`, `status`, `detail` e `instance`; añadir extensiones propias (`code`, `errors`) mediante propiedades.
- **MUST NOT** devolver trazas, nombres de clase, SQL ni mensajes de excepción internos en `detail`; los 500 llevan un mensaje genérico y un identificador de correlación.
- **MUST** registrar el error completo en el log con el mismo identificador de correlación (nivel ERROR solo para 5xx).
- **MUST** mapear errores de validación a 400 con la lista de campos inválidos; conflictos de negocio a 409; no encontrado a 404.
- **SHOULD** definir excepciones de dominio sin dependencia de Spring y traducirlas en el advice.
- **SHOULD** valorar `spring.mvc.problemdetails.enabled=true` para errores estándar de Spring MVC (verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08).

## Por qué
Un formato de error estándar permite a los clientes tratar fallos de forma uniforme y evita que cada endpoint invente el suyo. Filtrar trazas ayuda a un atacante a conocer librerías y estructura interna.

## Ejemplos
### Mal
```java
@ExceptionHandler(Exception.class)
ResponseEntity<String> handle(Exception e) {
    return ResponseEntity.status(500).body(e.toString()); // filtra detalles internos
}
```
### Bien
```java
@RestControllerAdvice
class ApiExceptionHandler extends ResponseEntityExceptionHandler {

    @ExceptionHandler(CustomerNotFoundException.class)
    ProblemDetail notFound(CustomerNotFoundException ex) {
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, "Customer not found");
        pd.setType(URI.create("https://errors.example.test/customer-not-found"));
        pd.setTitle("Customer not found");
        pd.setProperty("code", "CUSTOMER_NOT_FOUND");
        return pd;
    }

    @ExceptionHandler(Exception.class)
    ProblemDetail unexpected(Exception ex) {
        var correlationId = UUID.randomUUID().toString();
        log.error("Unexpected error correlationId={}", correlationId, ex);
        var pd = ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "Unexpected error");
        pd.setProperty("correlationId", correlationId);
        return pd;
    }
}
```

## Checklist de revisión
- [ ] Un único advice; respuestas `application/problem+json`.
- [ ] Ningún 5xx expone detalle interno; hay correlationId en respuesta y log.
- [ ] Validación -> 400 con campos; negocio -> 409/404.
- [ ] Hay tests del advice con `@WebMvcTest`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Tests del manejador de errores (formato y ausencia de trazas) | 1 | tests del proyecto generado |
| Regla Semgrep contra `e.getMessage()`/`printStackTrace` en respuestas | 1 | pendiente (`policies/semgrep/`) |
| Revisión de contrato de errores | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `controllers-and-validation`, `rest-design-guidelines`, `structured-logging`, `testing-slices`.
- Fuentes oficiales: RFC 9457 (rfc-editor.org/rfc/rfc9457) y Spring Framework Reference "Error Responses", consultadas 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
