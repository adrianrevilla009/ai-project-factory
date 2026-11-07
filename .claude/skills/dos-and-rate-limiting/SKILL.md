---
name: dos-and-rate-limiting
description: Usar al diseñar límites de tasa, tamaños, timeouts, paginación y protección frente a abuso o denegación de servicio en APIs Java/Spring.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Denegación de servicio y rate limiting

## Cuándo aplicar y cuándo no
- Aplica a endpoints públicos o de coste alto (búsqueda, exportación, login, subida de ficheros, GraphQL) y a consumidores de colas.
- No sustituye la protección de red (WAF/DDoS volumétrico), que es infraestructura y no se reproduce en local.

## Reglas
- **MUST** limitar tasa por identidad (usuario, cliente de API) y por IP como respaldo, con respuesta `429` y `Retry-After`.
- **MUST** límites más estrictos en login, recuperación de contraseña y endpoints que envíen correo o SMS.
- **MUST** paginación obligatoria con tamaño máximo en todo listado; sin "devolver todo".
- **MUST** fijar límites de tamaño de cuerpo, de ficheros y de profundidad/complejidad de consultas (GraphQL).
- **MUST** timeouts explícitos en clientes HTTP, BD y colas (`resilience-*`), con circuit breaker y bulkhead para aislar dependencias.
- **MUST NOT** ejecutar expresiones regulares con backtracking catastrófico sobre entrada del usuario (ReDoS); limitar longitud antes.
- **SHOULD** operaciones costosas asíncronas con cola acotada y rechazo cuando se llena.
- **SHOULD** el limitador compartido entre instancias (estado externo) si hay más de una réplica; un contador en memoria por pod no es un límite global.
- **SHOULD** métricas y alertas de 429, saturación de pools y latencia p99.

## Por qué
Un único cliente sin límite puede agotar hilos, conexiones o CPU y afectar a todos. El coste no está solo en volumen: una petición cara repetida basta. Los límites deben ser conocidos y documentados para el consumidor.

## Ejemplos
### Mal
```java
@GetMapping("/orders")
public List<Order> all() { return repo.findAll(); }    // sin paginación ni límite

RestClient c = RestClient.create();                    // sin timeouts configurados
```
### Bien
```java
@GetMapping("/orders")
public Page<OrderSummary> list(@PageableDefault(size = 20) @Max100 Pageable p) {
    return service.list(PageRequest.of(p.getPageNumber(), Math.min(p.getPageSize(), 100)));
}
```
```java
// Filtro con bucket por clave; si hay varias réplicas el estado debe ser compartido (p. ej. Redis).
if (!limiter.tryConsume(clientKey)) {
    response.setStatus(429);
    response.setHeader("Retry-After", "30");
    return;
}
```
Librería concreta (Bucket4j, Resilience4j RateLimiter o límite en gateway): TODO-VERIFY elección y versión. En local no se reproduce el límite del API Gateway/WAF de AWS.

## Checklist de revisión
- [ ] Todo listado paginado con máximo.
- [ ] Rate limit en login y endpoints caros; respuesta 429 con `Retry-After`.
- [ ] Timeouts configurados en todos los clientes.
- [ ] Límites de tamaño de cuerpo y ficheros.
- [ ] El límite funciona con varias réplicas.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `findAll()` sin `Pageable` en controladores | 1 | pendiente (`policies/semgrep/`) |
| Test de integración: la petición n+1 recibe 429 | 2 | tests del proyecto generado |
| Test de carga de saturación | 3 | skill `performance-testing` (bloque 08) |
| Revisión de límites en el diseño | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `owasp-top10-and-api-top10`, `file-upload-security`, `threat-modeling-stride`.
- Fuentes: OWASP API Security Top 10 (consumo de recursos sin restricciones), OWASP DoS Cheat Sheet — TODO-VERIFY URLs y nombre de categoría en la edición vigente.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
