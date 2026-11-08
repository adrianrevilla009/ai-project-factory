---
name: rest-design-guidelines
description: Usar al diseñar o revisar endpoints REST (recursos, verbos, códigos HTTP, errores) de un servicio Spring Boot.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Guías de diseño REST

## Cuándo aplicar y cuándo no
- Aplica a cualquier API HTTP/JSON expuesta a otros equipos, front-end o terceros.
- No aplica a gRPC (`grpc-protobuf`), GraphQL (`graphql`) ni a endpoints internos de actuator.

## Reglas
- **MUST** modelar sustantivos en plural y en minúsculas con guiones: `/orders/{orderId}/lines`; sin verbos en la ruta.
- **MUST** usar los verbos según su semántica (RFC 9110): GET seguro e idempotente, PUT/DELETE idempotentes, POST para crear o acciones no idempotentes, PATCH para cambios parciales.
- **MUST** devolver el código correcto: 201 + `Location` al crear, 204 sin cuerpo, 400 validación, 401/403 authn/authz, 404, 409 conflicto, 422 solo si se documenta, 429 límite.
- **MUST** devolver errores como `application/problem+json` (RFC 9457) con `type`, `title`, `status`, `detail` y un `traceId`.
- **MUST NOT** exponer entidades JPA: usar DTOs (`record`) con propiedades en `camelCase`.
- **MUST NOT** devolver 200 con un cuerpo de error ni filtrar stack traces.
- **SHOULD** usar ids opacos (UUID/ULID), fechas ISO 8601 en UTC y dinero como objeto `{amount, currency}` con decimal en texto.
- **SHOULD** modelar acciones de negocio como sub-recurso (`POST /orders/{id}/cancellation`) antes que verbos.
- **SHOULD** soportar `ETag`/`If-Match` en actualizaciones con riesgo de pisado.

## Por qué
Una API es un contrato difícil de retirar. Verbos y códigos consistentes permiten a clientes, proxies y caches comportarse bien sin documentación ad hoc. El formato de error único evita que cada cliente parsee N formatos.

## Ejemplos
### Mal
```java
@PostMapping("/createOrder")
public ResponseEntity<Object> create(@RequestBody OrderEntity order) {
    try { return ResponseEntity.ok(repo.save(order)); }
    catch (Exception e) { return ResponseEntity.ok(Map.of("error", e.getMessage())); }
}
```
### Bien
```java
@PostMapping("/orders")
ResponseEntity<OrderResponse> create(@Valid @RequestBody CreateOrderRequest req) {
    OrderResponse created = orderService.create(req);
    return ResponseEntity.created(URI.create("/orders/" + created.id())).body(created);
}

@ExceptionHandler(OrderNotFoundException.class)
ProblemDetail notFound(OrderNotFoundException ex) {
    ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.getMessage());
    pd.setType(URI.create("https://api.example.com/problems/order-not-found"));
    return pd;
}
```

## Checklist de revisión
- [ ] Rutas con sustantivos plurales, sin verbos.
- [ ] Códigos de estado correctos y `Location` en 201.
- [ ] Errores en `problem+json` con `traceId`.
- [ ] Ninguna entidad JPA en la firma del controlador.
- [ ] Contrato reflejado en OpenAPI (`openapi-contract-first`).

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Ruleset Spectral sobre el OpenAPI (nombres, códigos, problem+json) | 1 | pendiente: `policies/` (no existe aún) |
| Revisión de controladores por el agente `code-reviewer` | 3 | `.claude/agents/` (según Oleada) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `openapi-contract-first`, `pagination-filter-sort`, `idempotency-keys`, `api-versioning-deprecation`.
- Fuentes (verificadas 2026-11-07 solo por nombre de RFC; comprobar URL): RFC 9110 (HTTP Semantics), RFC 9457 (Problem Details); `ProblemDetail` de Spring Framework 6+ (comprobar versión del proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
