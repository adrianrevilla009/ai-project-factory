---
name: bff-and-api-gateway
description: Usar al diseñar el punto de entrada de APIs con API gateway, BFF por cliente y qué lógica puede vivir en cada uno.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# BFF y API Gateway

## Cuándo aplicar y cuándo no
- Aplica al exponer varios servicios a clientes distintos (web, móvil, terceros) o al decidir dónde centralizar autenticación, límites y enrutado.
- No aplica a un único servicio con un único cliente: un gateway añade un salto sin valor.

## Reglas
- **MUST** que el API gateway sólo haga preocupaciones transversales: enrutado, TLS, autenticación/validación de token, rate limiting, CORS, observabilidad.
- **MUST NOT** poner lógica de negocio en el gateway.
- **MUST** que un BFF pertenezca al equipo del cliente al que sirve y agregue/adapte datos para ese cliente.
- **MUST NOT** compartir un único BFF entre clientes con necesidades divergentes.
- **MUST** que el BFF delegue las reglas de negocio en los servicios; es adaptación, no dominio.
- **MUST** propagar identidad y cabeceras de trazado (`traceparent`) aguas abajo y aplicar timeouts y circuit breaker en las llamadas.
- **SHOULD** que la autorización fina siga en cada servicio (defensa en profundidad), no solo en el gateway.
- **SHOULD** versionar la API pública y gestionar su ciclo de vida en el gateway (`api-versioning-deprecation`).

## Por qué
El gateway evita duplicar preocupaciones transversales; el BFF evita que un API genérico obligue a los clientes a múltiples llamadas y sobreexposición. Con lógica de negocio en el gateway o BFF se crea un monolito distribuido difícil de cambiar.

## Ejemplos
### Mal
```java
// en el gateway: regla de negocio
if (order.total() > 1000 && customer.tier() == Tier.GOLD) discount = 0.1;
```
### Bien
```java
// BFF móvil: agrega y recorta, sin reglas de negocio
@GetMapping("/mobile/home")
HomeView home(@AuthenticationPrincipal Jwt jwt) {
    var orders = orderClient.recent(jwt.getSubject());      // timeout + circuit breaker
    var profile = profileClient.get(jwt.getSubject());
    return new HomeView(profile.displayName(), orders.stream().limit(3).map(OrderCard::from).toList());
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Pasarela para preocupaciones transversales (autenticación, límites, enrutamiento); BFF cuando cada cliente necesita una forma distinta de los datos.
- La pasarela no contiene lógica de negocio.
### Trampas frecuentes
- Lógica de negocio en la pasarela.
- Un BFF compartido por clientes con necesidades distintas.
- Pasarela que es un punto único de fallo sin alta disponibilidad.
- Transformaciones complejas que nadie versiona.
- Duplicar autenticación en la pasarela y en los servicios (confiar solo en una).
### Evidencia
- El contrato del BFF está versionado y probado con cada cliente.

## Checklist de revisión
- [ ] El gateway sólo contiene preocupaciones transversales.
- [ ] Cada BFF sirve a un cliente y tiene dueño.
- [ ] Sin reglas de negocio en gateway/BFF.
- [ ] Hay timeouts, circuit breaker y propagación de trazas.
- [ ] Los servicios autorizan por sí mismos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión humana de diseño; sin regla automática (pendiente) | 4 | ADR del proyecto generado |

En local no se reproduce un gateway gestionado de AWS (p. ej. API Gateway); se usa un equivalente de código abierto. Preparado para AWS, no verificado en real.

## Relacionados, fuentes y mantenimiento
- Relacionados: `microservices-decision-guide`, `rate-limiting-quotas`, `api-versioning-deprecation`, `strangler-fig-migration`.
- Fuentes: Sam Newman, "Backends For Frontends" (samnewman.io/patterns/architectural/bff).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
