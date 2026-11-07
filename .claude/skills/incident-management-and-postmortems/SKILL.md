---
name: incident-management-and-postmortems
description: "Usar al definir cómo se declara, gestiona y revisa un incidente operativo: roles, severidades, comunicación y postmortem sin culpas con acciones medibles."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Gestión de incidentes y postmortems

## Cuándo aplicar y cuándo no
- Aplica a incidentes de disponibilidad, rendimiento o datos en servicios con tier.
- No aplica a incidentes de seguridad con vulnerabilidades (ver `vulnerability-sla-and-incident-response`); se enlazan cuando coinciden.

## Reglas
- **MUST** definir severidades (SEV1-SEV4) ligadas al impacto en SLO y tier, con tiempos de respuesta y quién declara.
- **MUST** asignar roles al declarar: comandante de incidente, comunicaciones y operaciones; el comandante coordina, no depura.
- **MUST** mantener un canal único y una línea de tiempo con marcas horarias en UTC.
- **MUST** comunicar a interesados con una cadencia fija y a la página de estado (`status-page-and-comms`).
- **MUST** priorizar mitigar (rollback, failover, apagado de feature) sobre diagnosticar la causa raíz.
- **MUST** escribir un postmortem sin culpas para SEV1/SEV2 y cuando un incidente consuma presupuesto de error alto (`slo-error-budget-policy`), en un plazo definido (p. ej. 5 días laborables).
- **MUST** que cada acción del postmortem tenga dueño, fecha y ticket; las acciones sin dueño se consideran no aceptadas.
- **SHOULD** registrar detección, mitigación y recuperación (TTD/TTM/TTR) para tendencias.
- **MUST NOT** citar nombres para atribuir culpa ni incluir datos personales o secretos en el postmortem.

## Por qué
Durante un incidente el coste mayor es la confusión: quién decide, qué se sabe, qué se ha dicho al cliente. Los roles y el canal único lo reducen. El postmortem solo aporta si produce cambios verificables; un documento sin acciones con dueño es una anécdota. Los game days (`fault-injection-and-game-days`) ensayan este proceso.

## Ejemplos
### Mal
```text
Postmortem: "Error humano de Juan al desplegar. Acción: tener más cuidado."
```
### Bien
```markdown
# Postmortem INC-0042 (SEV2) - orders-api latencia
- Impacto: 38 min, 12% de peticiones > 2s; consumido 22% del presupuesto de error.
- Línea de tiempo (UTC): 09:02 alerta burn rate; 09:05 SEV2; 09:11 rollback; 09:40 normal.
- Causa contribuyente: migración sin límite de conexiones; el canary no cubría el caso.
- Qué fue bien / mal / suerte: ...
- Acciones:
  | Acción | Dueño | Fecha | Ticket |
  | Gate de canary con p95 por endpoint | platform-team | 2026-12-01 | PLAT-311 |
  | Límite de pool en plantilla de despliegue | orders-team | 2026-11-20 | ORD-190 |
```

## Checklist de revisión
- [ ] Severidades y roles definidos y conocidos.
- [ ] Plantilla de postmortem con acciones con dueño y fecha.
- [ ] Cadencia de comunicación y página de estado.
- [ ] Revisión de acciones abiertas en reunión periódica.
- [ ] Sin culpas personales ni secretos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Validador de plantilla de postmortem (campos obligatorios) | 1 | pendiente: `factory/validators/` |
| Revisión humana en la reunión de postmortem | 4 | proceso del equipo |

## Relacionados, fuentes y mantenimiento
- Relacionados: `slo-error-budget-policy`, `alert-routing-and-oncall`, `status-page-and-comms`, `fault-injection-and-game-days`, `failover-and-failback-runbooks`.
- Fuentes: Google SRE Book/Workbook (postmortem culture e incident response) — TODO-VERIFY URL concreta (no consultada 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
