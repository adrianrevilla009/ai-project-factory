---
name: rate-limiting-quotas
description: Usar al definir límites de tasa y cuotas por cliente de una API y cómo comunicarlos (429, Retry-After) en gateway o servicio.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Rate limiting y cuotas (contrato de API)

## Cuándo aplicar y cuándo no
- Aplica a APIs con más de un consumidor o expuestas fuera de la red de confianza.
- No aplica a la defensa anti-DoS ni límites de seguridad (ver `dos-and-rate-limiting`, bloque 07); aquí se define el contrato con el cliente.

## Reglas
- **MUST** definir límites por identidad de cliente (client id / tenant), no solo por IP, y por clase de operación (lectura vs escritura).
- **MUST** responder 429 con `Retry-After` (segundos) y cuerpo `problem+json` al superar el límite.
- **MUST** distinguir tasa (req/s, ráfaga) de cuota (volumen por día/mes) y documentar ambas en el contrato y en la guía del consumidor.
- **MUST** aplicar el límite de forma compartida entre réplicas (contador en gateway o almacén compartido), no en memoria por instancia.
- **MUST** definir el comportamiento si el almacén del contador falla (fail-open o fail-closed) y registrarlo como decisión.
- **SHOULD** exponer cabeceras informativas de límite restante; el formato `RateLimit-*` es un borrador IETF (TODO-VERIFY), documentar el que se use.
- **SHOULD** hacer que los clientes propios reintenten con backoff exponencial + jitter y respeten `Retry-After`.
- **MUST NOT** devolver 503 ni 403 para un límite de tasa.

## Por qué
Sin límites, un consumidor ruidoso degrada a todos. Un 429 con `Retry-After` permite autorregulación; contadores por instancia multiplican el límite efectivo por el número de réplicas.

## Ejemplos
### Mal
```java
private final Map<String, AtomicInteger> hits = new HashMap<>(); // por instancia, nunca se resetea
if (hits.merge(ip, 1, Integer::sum) > 100) throw new ResponseStatusException(HttpStatus.FORBIDDEN);
```
### Bien
```java
ResponseEntity<ProblemDetail> tooMany(long retryAfterSeconds) {
    ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.TOO_MANY_REQUESTS,
        "Límite de 100 req/min por cliente superado");
    return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS)
        .header(HttpHeaders.RETRY_AFTER, Long.toString(retryAfterSeconds))
        .contentType(MediaType.APPLICATION_PROBLEM_JSON)
        .body(pd);
}
```
Local: se puede probar con un límite en el gateway local o un filtro con almacén compartido; en AWS (API Gateway usage plans, WAF) está preparado para AWS, no verificado en real; no se reproducen en local.

## Checklist de revisión
- [ ] Límites por cliente y por clase de operación documentados.
- [ ] 429 + `Retry-After` + `problem+json`.
- [ ] Contador compartido entre réplicas; política fail-open/closed decidida.
- [ ] Clientes internos con backoff y jitter.
- [ ] Cuotas y límites en la documentación del consumidor.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Spectral: operaciones públicas declaran respuesta 429 | 1 | pendiente: `policies/` |
| Revisión de diseño de límites | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dos-and-rate-limiting`, `idempotency-keys`, `rest-design-guidelines`, `webhooks`.
- Fuentes: RFC 6585 (429), RFC 9110 (`Retry-After`); borrador IETF RateLimit header fields — TODO-VERIFY, no consultado el 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
