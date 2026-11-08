---
name: dr-tabletop-exercises
description: "Usar al planificar o documentar un simulacro de DR sobre papel (tabletop): escenarios, tiers RPO/RTO, roles y registro; sustituye lo que local no puede probar."
metadata:
  block: "29-cloud-readiness"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Simulacros de DR (tabletop)

## Cuándo aplicar y cuándo no
- Aplica a servicios con tier de resiliencia asignado y al diseño multi-región (primaria eu-west-1, secundaria eu-central-1, D6).
- No aplica a pruebas de failover reales: multi-región y DR no se reproducen en local y nada se despliega en AWS (ADR-0004). El tabletop es el único simulacro posible en la fábrica.

## Reglas
- **MUST** partir de `catalog/resilience-tiers.yaml`: el tier por defecto es 1 (warm standby, RPO aprox. minutos, RTO menor de 1 h). Los valores son de partida y los confirma negocio.
- **MUST** definir para cada ejercicio: escenario, tier, participantes con rol (facilitador, escriba, responsables de plataforma, datos y seguridad), supuestos y criterios de éxito.
- **MUST** recorrer, por componente, la acción de plano de datos que conmuta (promoción de Aurora Global Database, región de escritura de Global Tables, replicación de MSK y S3, Application Recovery Controller), según el principio de estabilidad estática.
- **MUST** incluir escenarios incómodos: la región caída contiene CI/CD o el estado de IaC; Vault independiente por región; reinicio de sesión de Keycloak.
- **MUST** registrar hallazgos con dueño y fecha, y convertirlos en tareas o ADR.
- **MUST** etiquetar el resultado como "simulacro documental; no verificado en real" (ver `maturity-labels`).
- **SHOULD** repetir el ejercicio al cambiar de tier o de topología, y al menos una vez al año (convención sugerida, a confirmar).
- **MUST NOT** presentar el tabletop como prueba de que el RTO/RPO se cumple.

## Por qué
La paridad local no cubre DR (ver `local-parity-matrix`). Un recorrido sobre papel detecta dependencias circulares, roles ambiguos y runbooks incompletos, a costa de reconocer que los tiempos reales son desconocidos.

## Ejemplos
### Mal
```markdown
DR probado: RTO de 15 minutos conseguido.
```
### Bien
```markdown
# Tabletop DR-2026-01
Escenario: pérdida de eu-west-1. Tier: 1 (RPO ~minutos, RTO < 1 h; objetivos de partida).
Resultado: simulacro documental; no verificado en real.
Hallazgo H1: el runner de CI depende de la región caída. Dueño: plataforma. Revisión: 2026-12-01.
Hallazgo H2: runbook de promoción de Aurora sin responsable de decisión.
```

## Checklist de revisión
- [ ] Escenario, tier, roles y criterios de éxito definidos.
- [ ] Recorrido por todos los componentes de `resilience-tiers.yaml`.
- [ ] Hallazgos con dueño y fecha.
- [ ] Etiqueta "no verificado en real" presente.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Afirmaciones honestas sobre RTO/RPO | 1 | `factory/validators/honest_claims.py` |
| Calidad del ejercicio y seguimiento | 3 | revisión humana (gate de fase) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `backup-and-restore`, `application-recovery-controller-and-health-checks`, `chaos-engineering`, `local-parity-matrix`.
- Fuentes: `catalog/resilience-tiers.yaml`, `catalog/parity-matrix.yaml`; disponibilidad de servicios en ambas regiones (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
