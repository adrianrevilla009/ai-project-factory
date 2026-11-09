---
name: lessons-learned-and-retro
description: "Usar tras un incidente, hito o iteración para hacer retrospectivas y postmortems sin culpables, con acciones con dueño y seguimiento."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Lecciones aprendidas y retrospectivas

## Cuándo aplicar y cuándo no
- Aplica tras incidentes con impacto, al cierre de hitos y en la cadencia periódica del equipo.
- No aplica a la gestión en vivo del incidente (ver `runbooks`, `alert-routing-and-oncall`).

## Reglas
- **MUST** hacer postmortem escrito para todo incidente con impacto a usuarios o pérdida de datos, en un plazo acordado (p. ej. 5 días laborables).
- **MUST** formato sin culpables: se analizan sistemas y decisiones, no personas.
- **MUST** incluir línea temporal, impacto, causas contribuyentes, qué funcionó, qué no y qué dio suerte.
- **MUST** que cada acción tenga dueño, fecha y enlace a su ticket; se revisan en la siguiente retro.
- **MUST** que las lecciones reutilizables actualicen skills, runbooks, checklist de PRR o ADRs; si no cambia nada, no se aprendió.
- **SHOULD** publicar los postmortems en `docs/postmortems/` para consulta del equipo.
- **MUST NOT** incluir secretos, datos personales ni nombres de personas como causa.
- **MUST NOT** cerrar la retro sin acciones concretas o sin decidir explícitamente no actuar.

## Por qué
Sin registro y seguimiento, los mismos fallos se repiten. Las acciones sin dueño no se hacen; los postmortems con culpables hacen que la gente oculte información.

## Ejemplos
### Mal
```markdown
Causa: Juan desplegó sin mirar. Acción: tener más cuidado.
```
### Bien
```markdown
# Postmortem 2026-11-03: pedidos duplicados (45 min)
## Impacto
312 pedidos duplicados; sin impacto económico.
## Línea temporal (UTC)
10:02 Despliegue 1.4.0 · 10:20 Alerta de duplicados · 10:47 Rollback
## Causas contribuyentes
- Reintentos del cliente sin `Idempotency-Key` obligatoria.
- Test de idempotencia ausente en CI.
## Acciones
| Acción | Dueño | Fecha | Ticket |
|---|---|---|---|
| Hacer obligatoria `Idempotency-Key` y test | dev-orders | 2026-11-17 | ORD-231 |
| Añadir ítem a la checklist de PRR | tech-lead | 2026-11-12 | ORD-232 |
```

## Checklist de revisión
- [ ] El postmortem no señala a personas.
- [ ] Hay impacto, línea temporal y causas contribuyentes.
- [ ] Cada acción tiene dueño, fecha y ticket.
- [ ] Se actualizó al menos un skill, runbook o checklist.
- [ ] Las acciones de la retro anterior se revisaron.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Plantilla de postmortem con campos obligatorios | 3 | pendiente: `docs/postmortems/TEMPLATE.md` en el proyecto generado |
| Seguimiento de acciones en la retro | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `runbooks`, `production-readiness-review`, `risk-register`, `chaos-engineering`, `alert-routing-and-oncall`.
- Fuentes: Google SRE Book, "Postmortem Culture: Learning from Failure".
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
