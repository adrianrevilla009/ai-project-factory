---
name: owasp-top10-and-api-top10
description: Usar al revisar o diseñar APIs y apps web frente a OWASP Top 10 y API Security Top 10; mapa de riesgos a skills y controles concretos.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# OWASP Top 10 y API Security Top 10

## Cuándo aplicar y cuándo no
- Aplica como lista de verificación al diseñar endpoints, en code review de seguridad y al priorizar hallazgos.
- No aplica como lista exhaustiva: es de concienciación; el detalle verificable está en `asvs-mapping`.

## Reglas
- **MUST** tratar la autorización a nivel de objeto (BOLA/IDOR) como riesgo n.º 1 de API: todo acceso por id valida propiedad o pertenencia al tenant (`authz-rbac-abac-rebac`).
- **MUST** denegar por defecto: ningún endpoint nuevo queda público salvo lista explícita.
- **MUST** exponer DTOs de respuesta explícitos; nunca serializar entidades JPA (exposición excesiva de propiedades).
- **MUST** aceptar solo los campos esperados en entrada (sin asignación masiva de campos como `role` o `tenantId`).
- **MUST** limitar tamaño, frecuencia y paginación (`dos-and-rate-limiting`).
- **MUST** mantener inventario de APIs y versiones expuestas; desactivar las obsoletas.
- **MUST** validar toda URL aportada por el usuario antes de consumirla (`deserialization-xxe-ssrf-traversal`).
- **SHOULD** revisar la lista vigente anualmente: las categorías cambian entre ediciones (TODO-VERIFY ediciones actuales de ambos Top 10).

## Por qué
La mayoría de brechas de API no son sofisticadas: faltan comprobaciones de propiedad, se devuelven campos de más o no hay límites. Un mapa riesgo -> skill -> control evita revisar de memoria.

## Ejemplos
### Mal
```java
@GetMapping("/orders/{id}")
public Order get(@PathVariable Long id) {
    return orderRepository.findById(id).orElseThrow();   // BOLA + entidad expuesta
}
```
### Bien
```java
@GetMapping("/orders/{id}")
public OrderResponse get(@PathVariable Long id, @AuthenticationPrincipal Jwt jwt) {
    return orderService.findForTenant(id, jwt.getClaimAsString("tenant_id"))
            .map(OrderResponse::from)
            .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
}
```
Mapa de uso rápido:
```text
Control de acceso roto      -> authz-rbac-abac-rebac, method-and-endpoint-security
Fallos criptográficos       -> crypto-tls-mtls-key-rotation, pii-and-data-classification
Inyección                   -> injection-families, input-validation-output-encoding
Configuración insegura      -> security-headers-cors-csrf, container-and-k8s-security
Componentes vulnerables     -> dependency-security, supply-chain
Fallos de autenticación     -> authn-oidc-oauth2, jwt-and-sessions
Registro y monitorización   -> audit-trail-and-security-logging
SSRF                        -> deserialization-xxe-ssrf-traversal
```

## Checklist de revisión
- [ ] Todo endpoint con id valida propiedad/tenant.
- [ ] Respuestas mediante DTO; entrada sin campos privilegiados.
- [ ] Hay límites de tamaño, paginación y tasa.
- [ ] No hay endpoints públicos fuera de la lista explícita.
- [ ] El inventario de APIs está al día.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep de misconfiguración Spring (CSRF, CORS, JWT sin verificar) | 1 | `policies/semgrep/spring-security-misconfig.yaml` (sin ejecutar, TODO-VERIFY) |
| Test de integración "otro tenant -> 404" por recurso | 2 | tests del proyecto generado |
| Regla ArchUnit: controladores no devuelven `@Entity` | 2 | pendiente (`policies/archunit/`) |
| Revisión humana con el mapa de arriba | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `asvs-mapping`, `authz-rbac-abac-rebac`, `injection-families`, `dos-and-rate-limiting`.
- Fuentes: OWASP Top 10 y OWASP API Security Top 10 (owasp.org) — TODO-VERIFY edición y numeración vigentes.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
