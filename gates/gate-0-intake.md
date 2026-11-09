# Gate 0 · Intake

**Propósito:** Validar requisitos, perfil de dominio y matriz de normativa antes de planificar.

**Aprobadores (ver `docs/operating-model/RACI.md`):** Experto de negocio (dominio); legal/cumplimiento (normativa); product owner (alcance)

## Condiciones de entrada
- El gate anterior tiene un registro de aprobación válido (`approval-record.schema.json`) — no aplica, es el primer gate.

## Criterios de salida
Ver `gates/checklists/gate-0.md`. Todos los puntos deben estar marcados o tener una excepción justificada.

## Procedimiento
1. El agente prepara la evidencia y se **detiene**. No avanza por su cuenta.
2. Una persona revisa y, si procede, crea el registro `approvals/gate-0.json` conforme al esquema.
3. El hook `enforce-gate-approval` solo permite pasar a la fase siguiente si el registro existe y es válido.
4. Si se rechaza, el registro lleva `decision: rejected` y los motivos; se vuelve a la fase.

## Reglas
- Un agente nunca crea ni edita registros de aprobación.
- Las afirmaciones sobre AWS respetan la política de honestidad (`docs/operating-model/`, skill `honest-claims-policy`).
