---
name: fault-injection-and-game-days
description: "Usar al planificar ejercicios de resiliencia: game days tabletop, inyección de fallos (Chaos Mesh, Toxiproxy, Chaos Monkey) y experimentos AWS FIS solo como diseño."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Inyección de fallos y game days

## Cuándo aplicar y cuándo no
- Aplica a la planificación trimestral de ejercicios de tier 0-2 y antes de comprometer un RTO.
- No aplica a ejecutar experimentos contra producción desde la fábrica: nunca despliega (D4).
- Ejercicio regional = **tabletop en papel** (matriz AWS-local: multi-región y DR solo simulacro documental). En local sí se puede usar Chaos Mesh (Kubernetes), Toxiproxy (red en tests) y Chaos Monkey for Spring Boot (aplicación).

## Reglas
- **MUST** definir por ejercicio: hipótesis de estado estable, alcance, condición de aborto, responsable, y registro de resultados.
- **MUST** empezar por tabletop: leer el runbook de `failover-and-failback-runbooks` con el equipo, cronometrar decisiones y anotar huecos.
- **SHOULD** progresar: local (Toxiproxy/Chaos Mesh) -> preproducción -> producción acotada, solo cuando exista entorno real.
- **MUST** incluir escenarios: pérdida de AZ, latencia/caída de dependencia, región primaria no disponible, lag de replicación alto, credenciales de BD caducadas tras failover (orden Aurora-Vault), registro de imágenes inaccesible.
- **MUST** tratar los experimentos AWS FIS (p. ej. aislar una réplica de Global Tables) como diseño documentado "no ejecutado"; el servicio es una opción de AWS, cuyas acciones concretas son TODO-VERIFY.
- **MUST** cerrar cada ejercicio con acciones asignadas y fecha; **MUST NOT** repetir el mismo ejercicio sin revisar las acciones previas.
- **SHOULD** ejercicios sin culpa; el resultado alimenta `incident-management-and-postmortems`.
- **MUST NOT** ejecutar chaos sin observabilidad ni plan de retorno.

## Por qué
Los RTO/RPO sin ejercicio son suposiciones. El tabletop es barato y descubre dependencias ocultas (quién tiene los permisos, dónde está el runbook) antes que cualquier herramienta de caos.

## Ejemplos
### Mal
```text
Game day: "apagar la región primaria a ver qué pasa" sin hipótesis ni aborto.
```
### Bien
```yaml
# gameday-2026-q4.yaml (plan en papel)
scenario: primary-region-unavailable
mode: tabletop
steady_state: "checkout p95 < 800 ms, error rate < 1 %"
hypothesis: "RTO <= 45 min con Aurora promovida antes de activar Vault DB engine"
abort: "no aplicable (papel)"
inject_local:
  - tool: toxiproxy
    target: orders-api -> postgres
    toxic: latency 2000ms
expected_findings: [runbook gaps, missing permissions]
actions_due: 2026-12-15
```

## Checklist de revisión
- [ ] Hipótesis, alcance y aborto definidos.
- [ ] Tabletop realizado y cronometrado.
- [ ] Escenario de orden Aurora-Vault incluido.
- [ ] Acciones con responsable y fecha.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Acta de ejercicio y seguimiento de acciones | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `failover-and-failback-runbooks`, `resilience-hub-assessments`, `incident-management-and-postmortems`, `tier-model-and-rpo-rto`.
- Fuentes: DynamoDB global tables y FIS (https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/V2globaltables_HowItWorks.html, 2026-11-07); resto: TODO-VERIFY.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
