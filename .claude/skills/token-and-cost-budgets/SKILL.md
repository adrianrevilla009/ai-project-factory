---
name: token-and-cost-budgets
description: "Usar al integrar un LLM en un servicio: límites de tokens, presupuesto de coste por petición/tenant, caché, enrutado de modelos y alertas de gasto."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Presupuestos de tokens y coste

## Cuándo aplicar y cuándo no
- Aplica a todo servicio que llama a un LLM de pago o auto-alojado (chat, RAG, extracción, agentes).
- No aplica a pruebas locales con modelos pequeños sin coste, salvo que se copien los límites al entorno real.

## Reglas
- **MUST** fijar `max_tokens` (salida) explícito en cada llamada y un tope de tokens de entrada; truncar o resumir el contexto antes de superarlo.
- **MUST** medir tokens de entrada y salida reales de cada respuesta (los devuelve la API) y registrarlos con `tenant`, `feature` y `model` como etiquetas de baja cardinalidad (ver `llm-observability`).
- **MUST** definir presupuesto por petición, por usuario/tenant y por día; al agotarlo, degradar (modelo menor, respuesta corta) o rechazar con error claro, nunca seguir sin límite.
- **MUST** poner tope a bucles de agentes: máximo de iteraciones, de llamadas a herramientas y de tokens acumulados por tarea.
- **MUST** pasar todas las llamadas por el `llm-gateway` para aplicar cuotas y registrar el gasto en un único sitio.
- **MUST** configurar alertas de gasto (umbral diario y salto respecto a la media) y un corte duro.
- **SHOULD** usar caché de prompt del proveedor para prefijos largos y estables, y caché de respuestas para entradas idénticas sin datos personales.
- **SHOULD** enrutar tareas simples a un modelo pequeño y reservar el grande para tareas difíciles, medido con `llm-evals`.
- **SHOULD** estimar el coste con la tabla de precios del proveedor leída de configuración, con fecha de vigencia.
- **MUST NOT** codificar precios en el código ni asumirlos estables; cambian con frecuencia.
- **MUST NOT** enviar documentos completos si basta un fragmento recuperado.

## Por qué
El coste de un LLM crece con tokens y con reintentos, y un bucle de agente o un usuario con entradas enormes puede multiplicarlo sin que se note hasta la factura. Un tope por petición y por tenant convierte el coste en un riesgo acotado. Los precios y límites exactos dependen del proveedor y del modelo: consultar su página oficial (TODO-VERIFY en cada revisión).

## Ejemplos
### Mal
```java
String answer = llm.complete(model, fullDocumentText + question); // sin max_tokens ni tope
while (!done) { answer = agent.step(answer); }                    // bucle sin límite
```
### Bien
```java
public final class BudgetGuard {
    private final int maxInputTokens;
    private final int maxOutputTokens;
    private final long dailyTenantLimit;

    public BudgetGuard(int maxInputTokens, int maxOutputTokens, long dailyTenantLimit) {
        this.maxInputTokens = maxInputTokens;
        this.maxOutputTokens = maxOutputTokens;
        this.dailyTenantLimit = dailyTenantLimit;
    }

    public LlmRequest check(LlmRequest req, long usedToday) {
        if (req.estimatedInputTokens() > maxInputTokens) {
            throw new BudgetExceededException("input too large: " + req.estimatedInputTokens());
        }
        if (usedToday + maxOutputTokens > dailyTenantLimit) {
            throw new BudgetExceededException("tenant daily budget exhausted");
        }
        return req.withMaxOutputTokens(maxOutputTokens);
    }
}
// agente: for (int i = 0; i < MAX_STEPS && budget.remaining() > 0; i++) { ... }
```

## Checklist de revisión
- [ ] Toda llamada define `max_tokens` y tope de entrada.
- [ ] Gasto etiquetado por tenant/feature/modelo.
- [ ] Presupuesto y degradación definidos; bucles de agente acotados.
- [ ] Alertas de gasto y corte duro configurados.
- [ ] Precios en configuración, no en código.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: llamada LLM sin `max_tokens` | 1 | pendiente (`policies/semgrep/`) |
| Test del `BudgetGuard` del gateway | 1 | pendiente (proyecto generado) |
| Revisión de presupuestos y alertas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `llm-gateway`, `llm-observability`, `llm-evals`, `finops-cost-management`, `rate-limiting`.
- Fuentes: documentación de precios y conteo de tokens del proveedor elegido (p. ej. https://platform.claude.com/docs/en/about-claude/pricing, consultada 2026-11-07; TODO-VERIFY cifras vigentes).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
