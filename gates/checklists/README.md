# checklists

Una lista de comprobación por gate. Es contra lo que el agente prepara la evidencia y lo que la persona revisa antes de aprobar.

| Fichero | Gate | Puntos |
|---|---|---|
| [`gate-0.md`](gate-0.md) | Intake | 8 |
| [`gate-1.md`](gate-1.md) | Plan | 6 |
| [`gate-2.md`](gate-2.md) | Implementación | 6 |
| [`gate-3.md`](gate-3.md) | Pull request | 5 |
| [`gate-4.md`](gate-4.md) | Release | 6 |
| [`gate-5.md`](gate-5.md) | Revisión cloud | 7 |

## Cómo se usan
- Cada punto debe estar **marcado con evidencia** (ruta, comando y resultado) o llevar una **excepción justificada**.
- El registro de aprobación (`approvals/gate-N.json`) cita el checklist en `checklist_ref`, así queda constancia de con qué versión de la lista se decidió.
- Los checklists son documentos de proceso: se cambian con un PR y una nota en el `CHANGELOG`, porque modificar uno cambia lo que significa aprobar.

Descripción de cada gate y del procedimiento: [`../README.md`](../README.md).
