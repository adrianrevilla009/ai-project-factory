# compliance-framework

Método para que un agente **prepare** el análisis normativo de un proyecto. No dictamina: una persona de legal o cumplimiento lo valida en el Gate 0 y queda registrado.

- `applicability-questionnaire.yaml` — preguntas (datos personales, sector, geografía, IA…) que acotan qué normas pueden aplicar.
- `research-protocol.md` — pasos obligatorios: buscar la fuente oficial, crear la ficha con `status: draft-to-confirm`, mapear obligaciones a controles.
- `regulation-entry.schema.yaml` — esquema de la ficha de una norma (URL oficial, fecha de verificación, estado).
- `obligation-to-control-mapping.schema.yaml` — esquema para vincular cada obligación con un control técnico.

Ninguna norma está redactada en este repo a propósito: se investiga por proyecto, con fuente oficial.
