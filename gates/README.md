# gates

Los seis puntos de control humano del ciclo de vida de un proyecto generado. Existen para que ninguna decisión importante la tome un agente por su cuenta: el agente prepara la evidencia, **se detiene**, y una persona decide.

## Los seis gates
| Gate | Cierra la fase | Qué se aprueba | Quién aprueba | Documento | Checklist |
|---|---|---|---|---|---|
| 0 | Intake | Requisitos, perfil de dominio y matriz de normativa | Product owner, con validación nominal de un experto de negocio y de legal o cumplimiento | [`gate-0-intake.md`](gate-0-intake.md) | [`checklists/gate-0.md`](checklists/gate-0.md) |
| 1 | Plan | Plan, arquitectura inicial y módulos | Tech lead, con arquitecto de solución y product owner | [`gate-1-plan.md`](gate-1-plan.md) | [`checklists/gate-1.md`](checklists/gate-1.md) |
| 2 | Implementación | El código implementado, antes de abrir el PR | Tech lead, con la revisión de `architecture-guardian` | [`gate-2-implementation.md`](gate-2-implementation.md) | [`checklists/gate-2.md`](checklists/gate-2.md) |
| 3 | Pull request | El PR, para fusionarlo | Revisor humano de código, con el security champion | [`gate-3-pull-request.md`](gate-3-pull-request.md) | [`checklists/gate-3.md`](checklists/gate-3.md) |
| 4 | Release | La versión candidata | Tech lead, con SRE y responsable de seguridad | [`gate-4-release.md`](gate-4-release.md) | [`checklists/gate-4.md`](checklists/gate-4.md) |
| 5 | Revisión cloud | La preparación para cloud; **no implica desplegar** | Platform engineer, con SRE, FinOps y seguridad | [`gate-5-cloud-readiness.md`](gate-5-cloud-readiness.md) | [`checklists/gate-5.md`](checklists/gate-5.md) |

La matriz completa de quién ejecuta, aprueba, es consultado e informado está en [`docs/operating-model/RACI.md`](../docs/operating-model/RACI.md).

## Cómo funciona un gate
1. **El agente prepara la evidencia** contra el checklist del gate (prompt `prompts/tasks/gate-evidence.md`): una tabla punto → evidencia → estado, con los bloqueantes, los riesgos y las excepciones propuestas. Después se detiene (skill `gate-protocol`).
2. **Una persona revisa** y, si procede, crea `approvals/gate-N.json` en el proyecto generado.
3. **El hook `enforce_gate_approval`** solo deja avanzar a la fase siguiente si ese registro existe y es válido.
4. Si se rechaza, el registro lleva `decision: rejected` y los motivos, y se vuelve a la fase.

Un agente **nunca** crea ni edita un registro de aprobación: lo impiden el hook y las reglas `deny` de `settings.json`, también desde la shell.

## El registro de aprobación
[`approval-record.schema.json`](approval-record.schema.json) es el esquema JSON que valida cada `approvals/gate-N.json`:

- **Obligatorios:** `gate` (0–5), `decision` (`approved`, `approved_with_conditions` o `rejected`), `approver` (nombre y rol de una persona), `timestamp`, `checklist_ref` (el checklist con el que se decidió) y `factory_version`.
- **Opcionales:** `conditions`, `exceptions` (con su justificación), `evidence` y `notes`.
- **Gate 0:** además, `domain_validated_by` y `compliance_validated_by` con el nombre de quien validó el dominio y la normativa.
- No admite campos desconocidos: un registro con campos de más se trata como inválido.

## Reglas
- El aprobador es siempre una persona.
- Las afirmaciones sobre AWS respetan la honestidad: «preparado para AWS, no verificado en real» (skill `honest-claims-policy`).
- Un punto del checklist sin cumplir exige una excepción justificada y registrada.
