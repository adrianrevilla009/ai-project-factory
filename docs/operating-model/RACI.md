# Modelo operativo y RACI de los gates

> Propuesta inicial a confirmar por el dueño de la fábrica. R = ejecuta, A = aprueba (único), C = consultado, I = informado.

| Gate | Agentes (R) | Aprueba (A) | Consultados (C) | Informados (I) |
|---|---|---|---|---|
| 0 Intake | business-analyst, domain-analyst, compliance-analyst | Product owner | Experto de negocio, legal/cumplimiento | Tech lead |
| 1 Plan | solution-architect, tech-lead | Tech lead | Product owner, SRE | Equipo |
| 2 Implementación | agentes de ingeniería, revisores | Tech lead | Architecture guardian | Product owner |
| 3 Pull Request | code-reviewer, security-reviewer | Revisor humano | Security champion | Equipo |
| 4 Release | delivery-manager, sre | Tech lead | Seguridad | Product owner |
| 5 Cloud readiness | platform-engineer, cloud-readiness-reviewer, finops-analyst | Platform lead | SRE, seguridad | Dirección |

Reglas: el aprobador debe ser una persona; ningún agente puede aprobar. El Gate 0 exige dos validaciones nominales adicionales (negocio y cumplimiento).
