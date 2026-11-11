# compliance-framework

El método con el que un agente **prepara** el análisis normativo de un proyecto. No dictamina: una persona de legal o de cumplimiento lo valida en el Gate 0 y queda registrado.

Ninguna norma está redactada en este repo a propósito (ADR-0025): la normativa cambia y depende del proyecto, así que se investiga cada vez, con fuente oficial, en lugar de fijarla aquí.

## Contenido
| Fichero | Qué es |
|---|---|
| `applicability-questionnaire.yaml` | Preguntas (jurisdicciones, sector regulado, datos personales, categorías especiales, IA…) que acotan qué normas pueden aplicar |
| `research-protocol.md` | Los pasos obligatorios: partir del cuestionario y de la normativa candidata del perfil de dominio, buscar la fuente oficial, crear la ficha con `status: draft-to-confirm`, mapear obligaciones a controles técnicos y pasar la validación humana |
| `regulation-entry.schema.yaml` | Esquema de la ficha de una norma: nombre, URL oficial, fecha de verificación y estado |
| `obligation-to-control-mapping.schema.yaml` | Esquema para vincular cada obligación con un control técnico concreto |

## Cómo encaja en el flujo
- Lo ejecuta el agente `compliance-analyst` en la fase de intake, a partir de la normativa candidata que sugiere [`domain-framework/`](../domain-framework/README.md).
- Las normas activan cosas concretas: por ejemplo, la residencia de datos se traduce en una barrera de regiones, y la supresión junto con event sourcing, en cifrado por sujeto.
- La validación la hace una persona en el [Gate 0](../gates/README.md) y se registra en `compliance_validated_by`.

## Reglas
- Una norma sin fuente oficial verificable no entra en la matriz.
- Toda ficha nace como `draft-to-confirm`; solo una persona de legal o cumplimiento la confirma.
- El agente no interpreta plazos ni sanciones como definitivos.
