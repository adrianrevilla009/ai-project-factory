---
name: human-in-the-loop
description: "Usar al diseñar flujos donde un LLM o agente propone acciones o decisiones que una persona debe aprobar, corregir o revisar antes de que tengan efecto."
metadata:
  block: "24-ai-engineering"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Human-in-the-loop (HITL)

## Cuándo aplicar y cuándo no
- Aplica a agentes con herramientas de escritura, clasificadores/extractores con confianza variable y decisiones con impacto sobre personas (crédito, empleo, salud, sanciones).
- No aplica a asistentes de solo lectura sin efectos laterales ni a tareas reversibles de bajo impacto donde basta el log (ver `llm-observability`).

## Reglas
- **MUST** clasificar cada acción del agente por impacto (lectura / reversible / irreversible / sobre personas) y exigir aprobación humana explícita en las dos últimas categorías.
- **MUST** separar "propuesta" de "ejecución": el modelo produce una propuesta persistida (`PENDING`), un humano la aprueba y solo entonces un componente determinista la ejecuta.
- **MUST** mostrar al revisor la evidencia (fuentes, campos extraídos, puntuación de confianza) y el diff exacto de lo que se va a ejecutar, no un resumen en lenguaje natural.
- **MUST** registrar quién aprobó, cuándo, qué versión de modelo/prompt y la decisión (aprobar / editar / rechazar) en un audit trail inmutable.
- **MUST** definir umbrales de confianza por tipo de caso; por debajo del umbral va a cola de revisión, por encima se muestrea (p. ej. auditoría aleatoria) en lugar de confiar a ciegas.
- **MUST NOT** permitir que el mismo agente apruebe su propia propuesta ni que una aprobación caduque sin revalidar si los datos cambiaron.
- **SHOULD** definir SLA y escalado de la cola de revisión y un comportamiento seguro por defecto (no ejecutar) al expirar.
- **SHOULD** medir tasa de edición/rechazo y tiempo de revisión; usarlos como señal de calidad en `llm-evals`.
- **SHOULD** diseñar para evitar el sesgo de automatización: ocultar la sugerencia hasta que el revisor forme criterio en casos de alto impacto, o exigir justificación al aprobar.

## Por qué
Un humano que aprueba a ciegas 500 propuestas al día es un sello de goma, no un control. La supervisión humana efectiva exige información, tiempo y autoridad para rechazar. Para sistemas de alto riesgo, el Reglamento (UE) 2024/1689 (AI Act) exige medidas de supervisión humana apropiadas (art. 14); el alcance legal concreto es borrador por confirmar con asesoría legal (ver `model-risk-and-ai-act-mapping`).

## Ejemplos
### Mal
```java
// El agente ejecuta directamente
@Tool("Refund order")
public void refund(String orderId, BigDecimal amount) {
    paymentClient.refund(orderId, amount);   // sin aprobación ni límite
}
```
### Bien
```java
@Tool("Propose a refund; a human must approve it")
public ProposalId proposeRefund(String orderId, BigDecimal amount, String rationale) {
    var proposal = new RefundProposal(orderId, amount, rationale,
            modelVersion, promptVersion, Status.PENDING);
    return proposalRepository.save(proposal).id();
}

// Endpoint distinto, con rol humano, ejecuta de forma determinista
@PreAuthorize("hasRole('REFUND_APPROVER')")
public void approve(ProposalId id, String approverId) {
    var p = proposalRepository.requirePending(id);
    if (p.proposedBy().equals(approverId)) throw new ForbiddenException("self-approval");
    paymentClient.refund(p.orderId(), p.amount());
    auditLog.record("REFUND_APPROVED", id, approverId, p.modelVersion(), p.promptVersion());
}
```

## Checklist de revisión
- [ ] Cada herramienta del agente tiene clase de impacto documentada.
- [ ] Las acciones irreversibles pasan por propuesta + aprobación.
- [ ] El revisor ve evidencia y diff, no solo un resumen.
- [ ] Hay audit trail con versión de modelo/prompt y decisión.
- [ ] Existe umbral de confianza, muestreo y SLA de cola.
- [ ] No hay auto-aprobación.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de herramientas del agente y de la separación propuesta/ejecución | 3 | agente `code-reviewer` |
| Regla ArchUnit "las herramientas de agente no llaman a puertos de escritura directamente" | 1 | pendiente (`policies/archunit/`) |
| Aprobación de diseño de flujos sobre personas | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `agents-and-tool-calling`, `llm-security`, `audit-trail-and-security-logging`, `model-risk-and-ai-act-mapping`, `llm-evals`.
- Fuentes: Comisión Europea, marco regulatorio de IA, https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai (consultado 2026-11-07; texto del art. 14 comprobar en EUR-Lex).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
