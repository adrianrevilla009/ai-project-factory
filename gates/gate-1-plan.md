# Gate 1 · Plan

**Propósito:** Aprobar plan, arquitectura inicial y módulos antes de implementar.

**Aprobadores (ver `docs/operating-model/RACI.md`):** Tech lead; arquitecto de solución; product owner

## Condiciones de entrada
- El gate anterior tiene un registro de aprobación válido (`approval-record.schema.json`).

## Criterios de salida
Ver `gates/checklists/gate-1.md`. Todos los puntos deben estar marcados o tener una excepción justificada.

## Procedimiento
1. El agente prepara la evidencia y se **detiene**. No avanza por su cuenta.
2. Una persona revisa y, si procede, crea el registro `approvals/gate-1.json` conforme al esquema.
3. El hook `enforce-gate-approval` solo permite pasar a la fase siguiente si el registro existe y es válido.
4. Si se rechaza, el registro lleva `decision: rejected` y los motivos; se vuelve a la fase.

## Reglas
- Un agente nunca crea ni edita registros de aprobación.
- Las afirmaciones sobre AWS respetan la política de honestidad (`docs/operating-model/`, skill `honest-claims-policy`).
