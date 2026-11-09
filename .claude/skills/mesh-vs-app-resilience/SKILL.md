---
name: mesh-vs-app-resilience
description: "Usar al decidir dónde implementar reintentos, timeouts y circuit breaking (malla Istio o aplicación) para no duplicar reintentos."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Resiliencia: malla o aplicación

## Cuándo aplicar y cuándo no
- Aplica a cualquier llamada síncrona entre servicios dentro de una malla Istio.
- No aplica a servicios fuera de la malla ni a mensajería asíncrona (ver `dlq-retries-poison-messages`).

## Reglas
- **MUST** asignar cada mecanismo a una sola capa y documentarlo: reintentos en una, no en ambas.
- **MUST NOT** activar reintentos en la malla (`retries`) y en el cliente (Resilience4j, Spring Retry) para la misma llamada: los intentos se multiplican (3 x 3 = 9).
- **MUST** reintentar solo operaciones idempotentes; para POST exigir clave de idempotencia (ver `idempotency-keys`).
- **MUST** respetar el presupuesto de tiempo: `timeout` total >= `attempts` x `perTryTimeout` y menor que el timeout del llamante.
- **SHOULD** dejar en la malla: timeouts de borde, `outlierDetection`, límites de conexión. **SHOULD** dejar en la aplicación: fallbacks de negocio, bulkheads, degradación funcional.
- **SHOULD** limitar `retryOn` a fallos de conexión y 503.
- **MUST** definir una política por defecto de la plataforma y excepciones documentadas.

## Por qué
Reintentos apilados convierten un fallo parcial en tormenta de peticiones que tumba al servicio que ya sufría. La malla no conoce semántica de negocio; la aplicación no ve el estado de red de todos los pods.

## Ejemplos
### Mal
```java
// Cliente con 3 reintentos...
@Retry(name = "orders", fallbackMethod = "fallback")   // maxAttempts: 3
public Order get(String id) { return client.get(id); }
```
```yaml
# ...y la malla también reintenta: hasta 9 intentos
http:
  - retries: { attempts: 3, perTryTimeout: 2s, retryOn: 5xx }
    route: [{ destination: { host: orders } }]
```
### Bien
```yaml
# Malla: solo timeout y expulsión; sin retries
http:
  - timeout: 3s
    route: [{ destination: { host: orders } }]
```
```java
// Aplicación: un único reintento, solo en lecturas idempotentes
@Retry(name = "orders")        // maxAttempts: 2 en application.yml
@CircuitBreaker(name = "orders", fallbackMethod = "cachedOrder")
public Order get(String id) { return client.get(id); }
```

## Checklist de revisión
- [ ] Cada llamada tiene reintentos en una sola capa.
- [ ] Solo operaciones idempotentes se reintentan.
- [ ] Timeouts coherentes de extremo a extremo.
- [ ] Documentada la política por defecto.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de VirtualService vs configuración Resilience4j | 3 | agente `code-reviewer` |
| Regla Conftest `retries` en mallas con Resilience4j (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `resilience`, `traffic-management`, `http-clients-and-timeouts`, `idempotency-keys`, `backpressure-and-bulkheads`.
- Fuentes: istio.io/latest/docs/concepts/traffic-management/#retries; documentación de Resilience4j; 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
