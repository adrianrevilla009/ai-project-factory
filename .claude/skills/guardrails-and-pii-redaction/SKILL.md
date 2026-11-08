---
name: guardrails-and-pii-redaction
description: "Usar al proteger entradas y salidas de un LLM: redacción de PII antes de enviar o registrar, filtros de contenido, validación de salida y comportamiento ante bloqueo."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Guardarraíles y redacción de PII

## Cuándo aplicar y cuándo no
- Aplica a todo flujo donde texto de usuarios o documentos llega a un LLM, o la salida del LLM llega a usuarios, logs o sistemas.
- No aplica a modelos puramente internos sin datos personales ni salida a usuarios; incluso entonces, mantener la redacción en logs.

## Reglas
- **MUST** clasificar los datos antes de enviarlos (ver `pii-and-data-classification`); categorías no permitidas nunca salen hacia el proveedor.
- **MUST** redactar o pseudonimizar PII en la entrada con tokens reversibles (`<PERSON_1>`) y mapa guardado solo en el servicio, si la respuesta debe re-personalizarse.
- **MUST** redactar PII en logs, trazas y datasets de evaluación; **MUST NOT** registrar prompts completos con datos reales en claro.
- **MUST** capas en orden: guardarraíl de entrada (PII, longitud, patrones de inyección), llamada, guardarraíl de salida (esquema, PII, contenido, fugas de prompt de sistema).
- **MUST** validar la salida estructurada contra esquema; si falla, reintento acotado y después error controlado, no texto libre al usuario.
- **MUST** definir el comportamiento al bloquear: mensaje neutro, código de error estable, evento de seguridad registrado (sin el contenido sensible).
- **SHOULD** combinar detectores deterministas (regex, validadores de IBAN/DNI, listas) con un detector de NER; ningún detector alcanza 100% de recall, así que medirlo con un conjunto de prueba.
- **SHOULD** usar guardarraíles del proveedor como capa adicional, nunca como única; no son reproducibles en local y deben poder desactivarse sin romper el servicio (en local, solo las capas propias).
- **MUST NOT** confiar en que "el modelo no repetirá" datos del contexto; el filtro de salida es obligatorio.
- **MUST NOT** afirmar cumplimiento RGPD/AI Act por tener filtros; es borrador por confirmar con asesoría legal (ver `model-risk-and-ai-act-mapping`).

## Por qué
Lo que entra en un prompt sale de tu perímetro y puede acabar en logs, cachés o entrenamiento de terceros. Y lo que sale del modelo es entrada no confiable para tu sistema. Los filtros fallan: por eso van por capas, se miden y tienen un camino de bloqueo definido.

## Ejemplos
### Mal
```java
log.info("prompt={}", userText);                       // PII en logs
return chat.prompt().user(userText).call().content();  // sin filtro ni de entrada ni de salida
```
### Bien
```java
public final class PiiRedactor {
    private static final Pattern EMAIL = Pattern.compile("[\\w.+-]+@[\\w-]+\\.[\\w.-]+");
    private static final Pattern IBAN  = Pattern.compile("\\b[A-Z]{2}\\d{2}[A-Z0-9]{11,30}\\b");

    public Redacted redact(String text) {
        var map = new LinkedHashMap<String, String>();
        var out = replace(IBAN, replace(EMAIL, text, "EMAIL", map), "IBAN", map);
        return new Redacted(out, map);   // el mapa nunca se registra ni se envía
    }
}

Answer answer(String userText) {
    var in = redactor.redact(userText);
    if (inputGuard.blocks(in.text())) return Answer.blocked("REQUEST_NOT_ALLOWED");
    var raw = chat.prompt().user(in.text()).call().entity(ClaimSummary.class); // esquema tipado
    var safe = outputGuard.check(raw);                                          // PII/contenido
    log.info("llm.ok redactions={}", in.map().size());                         // solo conteos
    return Answer.ok(redactor.restore(safe, in.map()));
}
```
Las regex de ejemplo no cubren todos los formatos; validar con un corpus propio. Detectores NER concretos (por ejemplo Presidio):.

## Checklist de revisión
- [ ] PII redactada antes de enviar y antes de registrar.
- [ ] Guardarraíl de salida y validación de esquema.
- [ ] Camino de bloqueo definido y probado.
- [ ] Recall/precisión de detectores medidos con muestra propia.
- [ ] Sin dependencia exclusiva de guardarraíles del proveedor.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: registro de prompt/entrada de usuario del LLM en logs | 1 | `policies/semgrep/llm-log-raw-prompt.yaml` |
| Test unitario del redactor con corpus de casos | 1 | tests del proyecto generado |
| Revisión de categorías de datos enviadas al proveedor | 3 | revisión humana (DPO/security-champions) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `pii-and-data-classification`, `llm-security`, `llm-gateway`, `structured-logging`, `model-risk-and-ai-act-mapping`, `prompt-injection-defense-for-agents`.
- Fuentes: OWASP Top 10 for LLM Applications (sensitive information disclosure, improper output handling) — comprobar edición; RGPD en EUR-Lex — borrador por confirmar.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
