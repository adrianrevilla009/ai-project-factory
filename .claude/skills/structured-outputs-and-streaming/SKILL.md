---
name: structured-outputs-and-streaming
description: "Usar cuando una respuesta de LLM alimenta código (JSON/esquema) o se envía al cliente en streaming (SSE): esquemas, validación, reintentos y cancelación."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Salidas estructuradas y streaming

## Cuándo aplicar y cuándo no
- Aplica cuando la salida del modelo la consume código (extracción, clasificación, llamadas a herramientas) o cuando se transmite token a token a un navegador.
- No aplica a texto libre que solo lee una persona y no se almacena ni se interpreta.

## Reglas
- **MUST** definir un esquema (JSON Schema o record Java) por cada salida consumida por código y validar la respuesta contra él antes de usarla, aunque el proveedor ofrezca modo estructurado.
- **SHOULD** usar la función nativa de salida estructurada del proveedor cuando exista (en la API de Claude: `output_config.format` con `type: "json_schema"`, y `strict: true` en herramientas; verificado en la documentación de Claude el 2026-11-08: GA desde 2026-01-29; la disponibilidad por modelo y por proveedor de nube se comprueba al elegirlos).
- **MUST** tratar el JSON generado como entrada no confiable: validar tipos, rangos y longitudes; reglas de negocio deterministas después (ver `intelligent-document-processing`).
- **MUST** gestionar fallos: truncado por `max_tokens`, rechazo del modelo, JSON inválido. Reintentar como máximo 1-2 veces con el error de validación; después, error controlado o revisión humana.
- **MUST** usar `enum` y campos cerrados (`additionalProperties: false`) para clasificaciones; incluir un valor explícito `unknown`.
- **MUST** en streaming: no parsear JSON parcial como definitivo; acumular hasta el evento de fin o usar un parser incremental tolerante y validar al cerrar.
- **MUST** en streaming: propagar cancelación del cliente al proveedor (cerrar el flujo) y poner timeouts de inactividad y totales.
- **MUST** enviar por SSE eventos tipados (`delta`, `done`, `error`) y filtrar con guardrails antes de mostrar si hay contenido sensible (ver `guardrails-and-pii-redaction`).
- **SHOULD** versionar el esquema y mantenerlo compatible hacia atrás (campos nuevos opcionales).
- **MUST NOT** ejecutar ni interpolar en SQL, shell o HTML ningún campo de la salida sin tratamiento (ver `llm-security`).

## Por qué
Un modelo puede devolver JSON truncado, con campos extra o con un valor fuera de rango; la salida estructurada reduce el problema pero no elimina la validación en el borde. El streaming mejora la latencia percibida, pero sin cancelación ni timeouts consume tokens (y dinero) por respuestas que nadie lee.

## Ejemplos
### Mal
```java
String json = llm.complete(prompt);                  // "devuelve JSON"
Order o = mapper.readValue(json, Order.class);       // sin esquema, sin control de fallos
repository.save(o);
```
### Bien
```java
public record Classification(Category category, double confidence) {
    public enum Category { INVOICE, CONTRACT, OTHER, UNKNOWN }
}

Classification classify(String text) {
    String lastError = null;
    for (int attempt = 0; attempt < 2; attempt++) {
        LlmResponse r = llm.complete(request(text, lastError));   // esquema en la petición
        if (r.stopReason() == StopReason.MAX_TOKENS) { lastError = "truncated"; continue; }
        try {
            Classification c = mapper.readValue(r.text(), Classification.class);
            if (c.confidence() < 0.0 || c.confidence() > 1.0) throw new IllegalArgumentException("range");
            return c;
        } catch (JsonProcessingException | IllegalArgumentException e) {
            lastError = e.getMessage();
        }
    }
    return new Classification(Classification.Category.UNKNOWN, 0.0);  // o enviar a revisión
}
```
Streaming: `SseEmitter emitter = new SseEmitter(60_000L); emitter.onTimeout(stream::cancel); emitter.onError(e -> stream.cancel());`

## Checklist de revisión
- [ ] Esquema definido y validado en el borde.
- [ ] Manejo de truncado, rechazo y reintento acotado.
- [ ] Streaming con cancelación, timeouts y eventos tipados.
- [ ] Sin parseo de JSON parcial como definitivo.
- [ ] Ningún campo del modelo llega a SQL/shell/HTML sin tratar.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Tests de contrato con respuestas inválidas/truncadas (mock del cliente) | 1 | pendiente (proyecto generado) |
| Revisión de esquemas, reintentos y cancelación | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `llm-security`, `llm-evals`, `guardrails-and-pii-redaction`, `token-and-cost-budgets`, `intelligent-document-processing`.
- Fuentes: https://platform.claude.com/docs/en/build-with-claude/structured-outputs; limitaciones de esquema y modelos soportados cambian.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
