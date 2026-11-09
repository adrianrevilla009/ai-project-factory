---
name: chatbot-design
description: "Usar al diseñar un chatbot o asistente conversacional corporativo: alcance, memoria, escalado a humano, transparencia y manejo de fallos."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Diseño de chatbots

## Cuándo aplicar y cuándo no
- Aplica a asistentes conversacionales (soporte, interno, RAG sobre documentación) con LLM.
- No aplica a pipelines no conversacionales (ver `intelligent-document-processing`) ni a la mecánica de recuperación (ver `rag-architecture`).

## Reglas
- **MUST** declarar un alcance explícito (temas permitidos, acciones permitidas, fuera de alcance) en el system prompt versionado y en la documentación del producto.
- **MUST** informar al usuario de que habla con una IA desde el primer mensaje (obligación de transparencia prevista en el AI Act).
- **MUST** ofrecer escalado a un humano en cualquier momento y automáticamente tras N fallos, baja confianza o temas sensibles (queja formal, salud, legal).
- **MUST** limitar la memoria: ventana de turnos acotada, resumen en lugar de historial completo, TTL y borrado a petición (ver `pii-and-data-classification`).
- **MUST** responder "no lo sé" con enlace a fuentes cuando la recuperación no encuentra evidencia, y citar fuentes en respuestas factuales.
- **MUST** autenticar al usuario antes de exponer datos personales y aplicar autorización en las herramientas, no en el prompt (ver `llm-security`).
- **MUST NOT** guardar conversaciones completas en logs sin redacción de PII ni base legal.
- **SHOULD** aplicar rate limiting por usuario y tope de tokens por conversación (ver `token-and-cost-budgets`).
- **SHOULD** recoger feedback (pulgar arriba/abajo) y convertir fallos en casos de `llm-evals`.
- **SHOULD** diseñar degradación: si el modelo falla, mostrar canal alternativo, no un error técnico.

## Por qué
Un chatbot sin alcance se convierte en un modelo genérico con la marca de la empresa: responde fuera de política y genera riesgo reputacional y legal. El escalado a humano y la transparencia son lo que distingue un asistente útil de un obstáculo. Las restricciones en el prompt no son un control de seguridad; la autorización debe vivir en el código.

## Ejemplos
### Mal
```text
System: Eres un asistente muy útil. Responde a todo lo que te pregunten.
(historial completo reenviado en cada turno; el usuario puede pedir "datos del cliente 1234")
```
### Bien
```yaml
# chatbot-policy.yaml (versionado junto al prompt)
scope:
  allowed_topics: [order-status, returns-policy, product-faq]
  forbidden: [legal-advice, medical-advice, other-customers-data]
disclosure: "Soy un asistente de IA. Puedes pedir hablar con una persona en cualquier momento."
memory: {max_turns: 10, summarize_after: 6, ttl_hours: 24}
escalation:
  triggers: [user_requests_human, low_confidence, three_failed_turns, sensitive_topic]
  handoff: human-support-queue
tools_authz: "ver OrderTools: filtran por customerId del token, nunca del prompt"
```
```java
@Tool("Get status of an order of the authenticated customer")
public OrderStatus orderStatus(String orderId, @AuthenticatedCustomer CustomerId customer) {
    return orders.findByIdAndCustomer(orderId, customer).orElseThrow(NotFoundException::new);
}
```

## Checklist de revisión
- [ ] Alcance y fuera de alcance documentados y versionados.
- [ ] Aviso de interacción con IA visible.
- [ ] Escalado a humano probado de extremo a extremo.
- [ ] Memoria acotada, con TTL y borrado.
- [ ] Herramientas autorizadas en código por identidad del token.
- [ ] Logs sin PII; feedback conectado a evals.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de política, prompts y herramientas | 3 | agente `code-reviewer` |
| Evals de fuera-de-alcance y escalado en CI | 1 | pendiente (ver `llm-evals`) |
| Revisión de transparencia y base legal | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rag-architecture`, `guardrails-and-pii-redaction`, `human-in-the-loop`, `llm-security`, `model-risk-and-ai-act-mapping`.
- Fuentes: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai (transparencia, consultado 2026-11-07). Borrador legal por confirmar.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
