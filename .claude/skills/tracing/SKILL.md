---
name: tracing
description: "Usar al añadir spans, propagación de contexto W3C y muestreo de trazas distribuidas (Tempo) en servicios HTTP, Kafka y asíncronos."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Trazas distribuidas

## Cuándo aplicar y cuándo no
- Aplica a spans manuales, propagación entre servicios/mensajes, muestreo y atributos de span.
- No aplica a la elección de instrumentación (`otel-java-agent-vs-sdk`) ni a métricas.

## Reglas
- **MUST** propagar contexto con W3C Trace Context (`traceparent`); **MUST NOT** inventar cabeceras propias de correlación.
- **MUST** propagar el contexto en hilos propios y `CompletableFuture`/executors (ver `async-and-context-propagation`); con virtual threads, verificar que se mantiene.
- **MUST** propagar el contexto en mensajes Kafka vía cabeceras (instrumentación del cliente o de Spring Kafka con observación activada).
- **MUST** crear spans manuales solo para operaciones de negocio con significado; nombre de baja cardinalidad (`order.reserve-stock`), nunca con IDs en el nombre.
- **MUST** marcar el span como error (estado y excepción) cuando falla; **MUST NOT** marcar error por respuestas 4xx esperadas de cliente.
- **MUST NOT** guardar PII, tokens ni payloads en atributos o eventos de span.
- **SHOULD** usar muestreo por cabecera del padre (`parentbased`) con ratio bajo en producción y 100 % en entornos de prueba; **SHOULD** considerar muestreo por cola en el Collector para conservar errores y trazas lentas.
- **SHOULD** enlazar con `span links` en consumidores por lotes en vez de un padre único.
- **SHOULD** habilitar exemplars o enlaces métrica-traza si el stack lo permite.

## Por qué
Una traza rota (contexto perdido en un executor o en Kafka) es peor que ninguna: induce a error. Los nombres con IDs generan cardinalidad inmanejable. Muestrear al 100 % en producción es caro; muestrear a ciegas pierde justo los errores, de ahí el muestreo por cola.

## Ejemplos
### Mal
```java
var span = tracer.spanBuilder("process order " + orderId).startSpan();
span.setAttribute("customer.email", email);
executor.submit(() -> service.process(orderId));   // contexto perdido
span.end();                                        // no se cierra si hay excepción
```
### Bien
```java
var span = tracer.spanBuilder("order.process").startSpan();
try (var scope = span.makeCurrent()) {
    span.setAttribute("acme.order.channel", channel);
    Context ctx = Context.current();
    executor.submit(ctx.wrap(() -> service.process(orderId)));
} catch (RuntimeException e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR);
    throw e;
} finally {
    span.end();
}
```
```yaml
# Muestreo en el Collector (processor tail_sampling, fragmento ilustrativo)
policies:
  - { name: errors, type: status_code, status_code: { status_codes: [ERROR] } }
  - { name: slow, type: latency, latency: { threshold_ms: 1000 } }
```

## Criterios de decisión y trampas
### Cómo decidir
- Propaga el contexto de traza en todas las fronteras (HTTP, mensajes, hilos) y crea spans en las operaciones que importan, no en todas.
- Muestrea con criterio: conserva errores y lentitud.
### Trampas frecuentes
- Contexto perdido en colas o tareas asíncronas.
- Spans para cada método.
- Muestreo uniforme que descarta los casos interesantes.
- Atributos con datos sensibles.
- Trazas sin relación con los registros.
### Evidencia
- Una traza completa de un flujo con mensajes y llamadas externas y con enlace a sus registros.

## Checklist de revisión
- [ ] Spans de baja cardinalidad en nombre; atributos sin PII.
- [ ] Contexto propagado en async y Kafka.
- [ ] Errores marcados; 4xx esperados no.
- [ ] Estrategia de muestreo declarada.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de spans manuales y propagación | 3 | agente `code-reviewer` |
| Test de integración que verifica un `traceId` único extremo a extremo (a incluir en el proyecto generado) | 1 | tests del proyecto generado |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `otel-fundamentals-and-semconv`, `otel-java-agent-vs-sdk`, `async-and-context-propagation`, `db-and-kafka-observability`, `virtual-threads`.
- Fuentes: OpenTelemetry (context propagation, sampling), W3C Trace Context.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
