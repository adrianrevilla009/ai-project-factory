# operating-model

Cómo se trabaja con la fábrica: las fases de un proyecto generado y quién es responsable de qué en cada gate.

| Documento | Qué define |
|---|---|
| [`project-lifecycle.md`](project-lifecycle.md) | El estado de un proyecto (`.factory/state.json` y `approvals/`), las fases (intake, plan, implementación, pull request, release, revisión cloud y cierre), los comandos de cada fase y las reglas del flujo, incluido que la infraestructura AWS se valida de forma estática y nunca se despliega |
| [`RACI.md`](RACI.md) | La matriz de responsabilidades de los seis gates: qué agentes ejecutan, quién aprueba (siempre una persona), quién es consultado y quién informado. Aprobada por el dueño de la fábrica |

## Cómo se relacionan con el resto
- Los gates se describen en [`gates/`](../../gates/README.md); aquí está el reparto de responsabilidades y el flujo en el que encajan.
- Los comandos de cada fase están en [`.claude/README.md`](../../.claude/README.md).
- Quien aprueba un gate deja un registro en `approvals/gate-N.json`, que el hook `enforce_gate_approval` valida.

Si cambia el reparto de responsabilidades, se actualiza el RACI en el mismo PR y se anota en el `CHANGELOG`.
