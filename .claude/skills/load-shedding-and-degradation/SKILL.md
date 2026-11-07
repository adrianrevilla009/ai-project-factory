---
name: load-shedding-and-degradation
description: "Usar al diseñar cómo un servicio rechaza o degrada carga bajo saturación o fallo parcial: prioridades, límites de concurrencia, modos degradados y retrocesos."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Load shedding y degradación controlada

## Cuándo aplicar y cuándo no
- Aplica a servicios con riesgo de saturación, a la región superviviente tras un failover y a dependencias blandas.
- No aplica a rate limiting por cliente/cuota comercial (ver `rate-limiting-quotas`, `dos-and-rate-limiting`) ni a patrones de aislamiento básicos (`backpressure-and-bulkheads`), que este skill complementa.

## Reglas
- **MUST** clasificar el tráfico por criticidad (p. ej. pagos > consulta > informes) y descartar primero lo menos crítico.
- **MUST** limitar la concurrencia por servicio y rechazar de forma temprana con `503` + `Retry-After` antes de agotar hilos o memoria.
- **MUST** definir niveles de degradación documentados por servicio (nivel 0 normal, 1 sin recomendaciones, 2 solo lectura, 3 solo tráfico crítico) y su disparador medible.
- **MUST** que los clientes usen timeouts, reintentos con backoff exponencial y jitter, y un presupuesto de reintentos; los reintentos sin límite amplifican la caída (`http-clients-and-timeouts`, `resilience`).
- **MUST** exponer métricas de descarte (cuántas peticiones, de qué clase) y alertar sobre ellas.
- **SHOULD** preferir degradar (caché obsoleta, valor por defecto) a fallar cuando la dependencia es blanda (`dependency-mapping-and-blast-radius`).
- **SHOULD** activar la degradación de forma automática por señal de saturación (latencia de cola, cola de peticiones) y permitir un interruptor manual.
- **MUST NOT** descartar peticiones no idempotentes tras haberlas procesado a medias; rechazar antes de empezar (`idempotency-keys`).
- **MUST** ensayar los modos degradados en un game day en papel (`fault-injection-and-game-days`).

## Por qué
Un sistema saturado que intenta servir todo acaba sirviendo nada: la latencia crece, los clientes reintentan y la carga se multiplica. Rechazar pronto lo menos importante protege lo crítico y acorta la recuperación. En un failover regional, la capacidad puede ser inferior al pico (`capacity-and-load-modeling`): la degradación es el plan, no un accidente.

## Ejemplos
### Mal
```java
// Sin límite: cada petición abre hilo y llama a la dependencia opcional
@GetMapping("/home")
Home home() {
    return new Home(catalog.top(), recommendations.forUser()); // si cae, todo cae
}
```
### Bien
```java
@GetMapping("/home")
Home home() {
    var top = catalog.top();                       // dependencia dura
    var recs = degradation.level() >= 1
        ? List.<Reco>of()                          // nivel 1: se omite
        : recommendations.forUserOrEmpty();        // timeout corto, fallback vacío
    return new Home(top, recs);
}

// Rechazo temprano por concurrencia
if (!bulkhead.tryAcquire()) {
    metrics.counter("shed.total", "class", requestClass).increment();
    return ResponseEntity.status(503).header("Retry-After", "5").build();
}
```
`bulkhead` y `degradation` son componentes propios del proyecto (por ejemplo con Resilience4j; TODO-VERIFY versión).

## Checklist de revisión
- [ ] Clases de tráfico por criticidad definidas.
- [ ] Niveles de degradación documentados con disparadores.
- [ ] Rechazo temprano con `Retry-After`; reintentos acotados.
- [ ] Métricas de descarte y alertas.
- [ ] Modo degradado ensayado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Semgrep: clientes HTTP sin timeout | 1 | `policies/semgrep/spring-http-client-without-timeout.yaml` |
| Semgrep: executors sin límite | 1 | `policies/semgrep/java-unbounded-executors.yaml` |
| Revisión humana de niveles de degradación | 4 | PR / gate |

## Relacionados, fuentes y mantenimiento
- Relacionados: `backpressure-and-bulkheads`, `resilience`, `capacity-and-load-modeling`, `dependency-mapping-and-blast-radius`, `static-stability-and-cell-architecture`.
- Fuentes: Amazon Builders' Library "Using load shedding to avoid overload" — TODO-VERIFY URL (no consultada 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
