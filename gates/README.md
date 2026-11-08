# gates

Seis puntos de control humano. El agente prepara la evidencia y se detiene; una persona decide.

| Gate | Fase que cierra | Documento | Checklist |
|---|---|---|---|
| 0 | Intake (dominio y normativa validados) | `gate-0-intake.md` | `checklists/gate-0.md` |
| 1 | Plan y arquitectura inicial | `gate-1-plan.md` | `checklists/gate-1.md` |
| 2 | Implementación | `gate-2-implementation.md` | `checklists/gate-2.md` |
| 3 | Pull request | `gate-3-pull-request.md` | `checklists/gate-3.md` |
| 4 | Release | `gate-4-release.md` | `checklists/gate-4.md` |
| 5 | Cloud readiness | `gate-5-cloud-readiness.md` | `checklists/gate-5.md` |

Cada gate aprobado deja `approvals/gate-N.json`, validado contra `approval-record.schema.json` (aprobador, rol, fecha, decisión, referencia al checklist; el gate 0 añade quién validó dominio y normativa). El hook `enforce_gate_approval` bloquea editar código si faltan registros válidos, y las reglas de `settings.json` impiden que un agente escriba en `approvals/`.

Los aprobadores de cada gate están en [`docs/operating-model/RACI.md`](../docs/operating-model/RACI.md) como propuesta pendiente de confirmar.
