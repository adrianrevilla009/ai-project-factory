---
name: backpressure-and-bulkheads
description: Usar al limitar carga y aislar fallos - colas acotadas, rate limiting, bulkheads (Resilience4j), rechazo temprano y degradación.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Backpressure y bulkheads

## Cuándo aplicar y cuándo no
- Aplica a servicios que llaman a dependencias externas, consumen colas o reciben ráfagas.
- No aplica a la política completa de circuit breaker/retry (ver `resilience`); este skill cubre limitar concurrencia y carga.

## Reglas
- **MUST** acotar toda cola, buffer y pool; ante saturación, rechazar rápido (429/503) en vez de acumular.
- **MUST** aplicar un bulkhead por dependencia (semáforo o pool dedicado) para que una dependencia lenta no consuma todos los hilos.
- **MUST** poner timeout en cada llamada saliente; sin timeout el bulkhead se llena igual.
- **MUST** que los consumidores de mensajes limiten el prefetch/`max.poll.records` y la concurrencia al ritmo que el proceso aguanta.
- **SHOULD** usar Resilience4j `Bulkhead`/`ThreadPoolBulkhead` y `RateLimiter`.
- **SHOULD** con virtual threads, limitar con `Semaphore` la concurrencia hacia el recurso (ver `virtual-threads`).
- **MUST** definir degradación explícita (respuesta parcial, caché, valor por defecto) cuando el bulkhead rechaza.
- **MUST NOT** reintentar sin límite ni sin *jitter* contra una dependencia saturada (amplifica la caída).
- **SHOULD** medir saturación (cola, rechazos, esperas) y alertar antes del límite.

## Por qué
Sin límites, la sobrecarga se propaga: la dependencia lenta retiene hilos, el pool se agota, la cola crece y todo el servicio cae, incluidas rutas sanas. Rechazar pronto mantiene la latencia de lo aceptado y da señal al llamante.

## Ejemplos
### Mal
```java
@Bean Executor reportExecutor() {
    return Executors.newCachedThreadPool();       // sin cota
}
String callPartner(String id) {
    return restClient.get().uri("/p/{id}", id).retrieve().body(String.class); // sin timeout ni límite
}
```
### Bien
```yaml
resilience4j:
  bulkhead:
    instances:
      partner:
        max-concurrent-calls: 20
        max-wait-duration: 0ms        # rechazar al instante
```
```java
@Bulkhead(name = "partner", fallbackMethod = "partnerFallback")
String callPartner(String id) { return partnerClient.fetch(id); } // cliente con timeout 2s

String partnerFallback(String id, BulkheadFullException e) {
    throw new ServiceUnavailableException("partner busy"); // 503 + Retry-After
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Cola acotada con rechazo explícito antes que cola infinita: un sistema que no puede rechazar acaba cayendo.
- Aísla recursos por dependencia (bulkhead) para que una lenta no consuma todo el sistema.
### Trampas frecuentes
- Colas sin límite que ocultan la saturación hasta que es tarde.
- Un único pool de conexiones para todas las dependencias.
- Reintentos que multiplican la carga sobre un servicio ya saturado.
- Rechazar sin informar al cliente de cuándo reintentar.
- Límites copiados sin medir.
### Evidencia
- Una prueba de carga que satura una dependencia y muestra que el resto del sistema sigue respondiendo.

## Checklist de revisión
- [ ] Colas y pools acotados.
- [ ] Bulkhead y timeout por dependencia.
- [ ] Degradación definida al rechazar.
- [ ] Consumidores con concurrencia/prefetch limitados.
- [ ] Métricas de saturación.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep contra executors sin cota | 1 | `policies/semgrep/java-unbounded-executors.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Test de carga/saturación | pendiente | tests del proyecto generado |
| Revisión de dependencias salientes | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `threads-executors-and-pools`, `resilience`, `http-clients-and-timeouts`, `virtual-threads`.
- Fuentes: documentación de Resilience4j (Bulkhead, RateLimiter).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
