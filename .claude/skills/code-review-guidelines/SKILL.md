---
name: code-review-guidelines
description: "Usar al revisar un pull request o preparar uno para revisión: qué mirar, en qué orden, tamaño del PR y cómo formular comentarios."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Guía de revisión de código

## Cuándo aplicar y cuándo no
- Aplica a todo PR hacia la rama principal, ya sea de personas o de agentes.
- No aplica a cambios generados mecánicamente (formato, bump de Renovate con CI verde) salvo que toquen lógica.

## Reglas
- **MUST** revisar en este orden: (1) corrección y requisitos, (2) tests, (3) seguridad, (4) diseño y límites de capas, (5) legibilidad, (6) estilo (lo automatizable lo decide la herramienta, no el revisor).
- **MUST** que el PR sea revisable: un solo propósito, descripción con el porqué y enlace al requisito. Objetivo orientativo: menos de 400 líneas cambiadas; si es mayor, dividirlo.
- **MUST** que CI esté en verde antes de pedir revisión humana.
- **MUST** que cada comentario bloqueante indique el riesgo concreto; el resto se marca `nit:` o `suggestion:`.
- **MUST** verificar que hay test que falla sin el cambio (o justificación explícita).
- **MUST NOT** aprobar sin haber leído el diff completo ni aprobar tu propio PR.
- **MUST NOT** aceptar `@SuppressWarnings`, `@Disabled` o exclusiones de análisis sin motivo escrito.
- **SHOULD** responder a una revisión en menos de un día laborable; **SHOULD** preferir pair/revisión síncrona para cambios de diseño grandes.
- **SHOULD** que el autor se autorrevise el diff antes de pedir revisión.

## Por qué
La revisión es el último filtro humano. Un PR grande o sin contexto recibe aprobaciones superficiales; los comentarios sin riesgo explícito generan discusión en vez de mejora. Delegar el estilo a herramientas libera atención para lo que las máquinas no ven (diseño, intención).

## Ejemplos
### Mal
```text
LGTM
```
```text
Esto no me gusta, hazlo de otra forma.
```
### Bien
```text
blocking: `OrderService.cancel` llama a `paymentClient.refund` dentro de la
transacción; si el commit falla, el reembolso ya salió. Mover tras commit
(outbox o @TransactionalEventListener(phase = AFTER_COMMIT)).

nit: renombrar `tmp` a `pendingItems`.
```
### Plantilla de descripción de PR
```markdown
## Qué y por qué
## Cómo se ha probado
## Riesgos / rollback
## Checklist: tests, docs, ADR si hay decisión nueva
```

## Criterios de decisión y trampas
### Cómo decidir
- Cambios de diseño o de alto riesgo: revisión síncrona o con la persona que mejor conoce la zona; el resto, PR pequeño y asíncrono.
- Automatiza lo mecánico (formato, estilo) para que el revisor humano mire corrección, seguridad y diseño.
### Trampas frecuentes
- PRs gigantes que se aprueban sin leerse.
- Revisar solo el estilo.
- Bloquear por preferencias personales sin riesgo concreto.
- Aprobar sin leer los tests.
- Un único revisor posible para una zona (punto único de fallo).
- Revisiones lentas, que empujan a PRs aún mayores.
### Evidencia
- El tiempo hasta la primera respuesta y el tamaño mediano de los PR, medidos.

## Checklist de revisión
- [ ] PR con un único propósito y descripción con el porqué.
- [ ] CI verde; tests nuevos que cubren el comportamiento.
- [ ] Sin secretos, sin inyección, validación de entradas (ver `injection-families`).
- [ ] Respeta capas y puertos (ver `layering-rules-archunit`).
- [ ] Comentarios bloqueantes con riesgo explícito.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión por agente `qa-engineer` / revisión humana obligatoria | 3 | `.claude/agents/quality/qa-engineer.md` |
| Protección de rama y aprobación requerida | 4 | configuración del repositorio del proyecto generado (pendiente) |
| Plantilla de PR | 3 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `static-analysis`, `code-smells-and-refactoring`, `test-strategy`, `verify-before-asserting`.
- Fuentes: guía de revisión de Google Engineering Practices (https://google.github.io/eng-practices/review/, consultada 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
