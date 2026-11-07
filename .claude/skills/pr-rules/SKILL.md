---
name: pr-rules
description: "Usar al abrir, describir o revisar un pull request: tamaño, plantilla de descripción, checks requeridos, aprobaciones y cuándo no se puede hacer merge."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Reglas de pull request

## Cuándo aplicar y cuándo no
- Aplica a todo cambio que llegue a `main` (código, IaC, docs, configuración de agentes).
- No aplica a commits automáticos de bots de dependencias, que siguen el mismo flujo pero con descripción generada.

## Reglas
- **MUST** abrir PR pequeño y con un único propósito: orientativamente < 400 líneas cambiadas (sin código generado ni lockfiles).
- **MUST** titular el PR en formato Conventional Commits (será el mensaje del squash).
- **MUST** incluir en la descripción: qué cambia, por qué, cómo se probó, riesgos/rollback y enlace al ticket.
- **MUST** tener los checks requeridos en verde (build, tests, lint, SAST, escaneo de dependencias) antes de pedir revisión.
- **MUST** tener al menos una aprobación de alguien distinto del autor; cambios de seguridad, datos o IaC requieren revisor de ese ámbito.
- **MUST** resolver (no ignorar) todos los comentarios bloqueantes antes del merge.
- **MUST** actualizar docs/ADR/changelog afectados en el mismo PR.
- **MUST NOT** hacer merge con checks fallando, con `--no-verify` previo ni saltándose la protección de rama.
- **MUST NOT** aprobar un PR propio ni aprobar sin haber leído el diff completo.
- **SHOULD** usar PR en borrador para pedir feedback temprano.
- **SHOULD** responder revisiones en menos de un día laborable.

## Por qué
Los PR grandes se revisan mal: la atención cae con el tamaño y los defectos pasan. Una descripción con el porqué y el plan de rollback permite revisar la intención, no solo el diff. Las aprobaciones humanas son un gate; la fábrica nunca las simula (CLAUDE.md, regla 3).

## Ejemplos
### Mal
```markdown
Title: updates
Body: (vacío)
Diff: 2.300 líneas, 41 ficheros, tres temas mezclados
```
### Bien
```markdown
Title: feat(refunds): add partial refund endpoint

## Qué y por qué
Añade POST /refunds con importe parcial (PAY-123).

## Cómo se probó
- Tests unitarios y de integración con Testcontainers.
- Contrato Pact actualizado.

## Riesgo y rollback
Detrás del flag features.refunds.enabled (apagado por defecto). Rollback: apagar el flag.

## Checklist
- [x] Docs/ADR actualizados  - [x] Changelog  - [x] Sin secretos
```

## Checklist de revisión
- [ ] Título convencional y descripción completa.
- [ ] Tamaño razonable y un solo propósito.
- [ ] Checks en verde; sin saltos de protección.
- [ ] Aprobación independiente (y de ámbito si aplica).
- [ ] Docs, ADR y changelog actualizados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook que impide cerrar la sesión sin actualizar docs tras cambiar código | 2 | `.claude/hooks/stop/require_docs_updated.py` |
| Hook que impide cerrar con tests en rojo | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Plantilla de PR (`.github/pull_request_template.md`) y branch protection en el proyecto generado | 2 | pendiente (proyecto generado) |
| Revisión del PR por agente | 3 | agente `code-reviewer`; comando `.claude/commands/03-pull-request` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `code-review-guidelines`, `conventional-commits`, `git-workflow`, `definition-of-ready-and-done`, `quality-gates`.
- Fuentes: práctica interna; umbral de tamaño es heurística del equipo, no norma (TODO-VERIFY si se adopta un valor distinto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
