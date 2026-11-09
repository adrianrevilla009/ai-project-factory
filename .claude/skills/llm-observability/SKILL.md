---
name: llm-observability
description: "Usar al instrumentar llamadas a LLM en una aplicación: trazas, tokens, latencia, coste, calidad y privacidad de prompts."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Observabilidad de aplicaciones con LLM

## Cuándo aplicar y cuándo no
- Aplica a servicios que llaman a modelos de lenguaje (chat, embeddings, agentes, RAG) del proyecto generado.
- No aplica a la seguridad frente a inyección de prompts (ver `llm-security`) ni a observabilidad de los agentes de la fábrica.

## Reglas
- **MUST** envolver cada llamada a un modelo en un span con atributos de modelo, proveedor, tokens de entrada y salida, motivo de finalización y estado de error, siguiendo las convenciones semánticas de GenAI (estado Development en OpenTelemetry a 2026-11-08, así que los nombres como `gen_ai.request.model` y `gen_ai.usage.input_tokens` pueden cambiar).
- **MUST** exponer métricas: latencia (histograma) incluyendo tiempo hasta el primer token si hay streaming, tokens consumidos, errores por tipo, reintentos y rate limits.
- **MUST** estimar coste por petición a partir de tokens y tarifa configurable; el coste es una métrica, no un cálculo manual.
- **MUST NOT** registrar prompts ni respuestas completos por defecto: pueden contener PII o secretos. Si se capturan para depuración, deben ser opt-in, muestreados, enmascarados y con retención corta.
- **MUST NOT** usar prompt, usuario o ID de conversación como tag de métrica.
- **SHOULD** trazar cada paso de un agente/RAG (recuperación, llamada a herramienta, llamada a modelo) como spans hijos de la petición.
- **SHOULD** medir calidad con evaluaciones (conjunto dorado, comprobaciones automáticas, feedback de usuario) y versionar prompts, para correlacionar regresiones con cambios.
- **SHOULD** fijar timeouts, presupuestos de tokens y alertas de coste y de tasa de error (ver `http-clients-and-timeouts`).

## Por qué
Un LLM es una dependencia lenta, cara y no determinista: sin tokens, latencia y coste por petición se ve la factura, no la causa. Los prompts son datos de usuario; tratarlos como logs normales es una fuga de privacidad.

## Ejemplos
### Mal
```java
log.info("prompt={} response={}", prompt, response);   // PII en logs
registry.counter("llm.calls", "user", userId).increment();
```
### Bien
```java
var span = tracer.spanBuilder("chat " + model).startSpan();   // nombre acotado
try (var scope = span.makeCurrent()) {
    var result = client.chat(request);
    span.setAttribute("gen_ai.request.model", model);                       // gen_ai.*: estado Development
    span.setAttribute("gen_ai.usage.input_tokens", result.inputTokens);   // gen_ai.*: estado Development
    span.setAttribute("gen_ai.usage.output_tokens", result.outputTokens); // gen_ai.*: estado Development
    registry.counter("llm.tokens", "model", model, "direction", "input").increment(result.inputTokens());
    registry.counter("llm.tokens", "model", model, "direction", "output").increment(result.outputTokens());
} catch (RuntimeException e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR);
    throw e;
} finally {
    span.end();
}
```

## Checklist de revisión
- [ ] Span por llamada con modelo y tokens.
- [ ] Métricas de latencia, tokens, errores y coste.
- [ ] Prompts/respuestas no se registran por defecto.
- [ ] Sin IDs de usuario ni prompts como tags.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de qué se registra de prompts y respuestas | 3 | agente `code-reviewer` |
| Regla Semgrep contra `log.*` con variables `prompt`/`response` (pendiente) | 1 | `policies/semgrep/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `llm-security`, `pii-and-data-classification`, `tracing`, `metrics-micrometer`, `http-clients-and-timeouts`.
- Fuentes: OpenTelemetry (semantic conventions for GenAI, estado Development en el registro de atributos de opentelemetry.io, verificado el 2026-11-08); fijar la versión de semconv y revisar los nombres al actualizar.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
