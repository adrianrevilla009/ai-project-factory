---
name: production-readiness-review
description: "Usar antes de dar un servicio por apto para operar (PRR): checklist de observabilidad, resiliencia, seguridad, datos y operación, con honestidad sobre AWS."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Production Readiness Review (PRR)

## Cuándo aplicar y cuándo no
- Aplica antes del primer lanzamiento de un servicio y ante cambios mayores (nueva dependencia crítica, nuevo almacén de datos, cambio de SLO).
- No aplica a cambios menores ya cubiertos por `pr-rules` y `definition-of-ready-and-done`.

## Reglas
- **MUST** ejecutar la PRR como checklist escrita, con evidencia enlazada por ítem (dashboard, test, runbook, ADR), no como conversación.
- **MUST** cubrir: SLOs y alertas por síntoma, logs/trazas/métricas, health checks, límites y timeouts, degradación controlada, backup y restore probado, capacidad, seguridad (authn/z, secretos, SBOM), runbooks y guardia asignada, plan de rollback.
- **MUST** que cada ítem sea Cumple / No cumple / No aplica (con motivo); un "No cumple" crítico bloquea el lanzamiento o requiere riesgo aceptado en `risk-register`.
- **MUST** que la aprobación sea humana; el agente prepara la checklist, nunca la firma (gates humanos).
- **MUST** etiquetar la madurez de la infraestructura: "validada estáticamente" / "preparado para AWS, no verificado en real". La fábrica nunca despliega (ADR-0004).
- **SHOULD** repetir la PRR ante cambios mayores y cada año.
- **MUST NOT** afirmar que algo está verificado en AWS real ni usar fórmulas de "listo" sin evidencia.

## Por qué
Los fallos en producción suelen venir de lo no mirado: alertas sin runbook, restore nunca probado, timeouts por defecto. Una checklist con evidencia vuelve explícito lo que falta y deja registro de quién aceptó qué riesgo.

## Ejemplos
### Mal
```markdown
PRR orders-service: todo ok, se puede lanzar.
```
### Bien
```markdown
# PRR orders-service v1.0 (2026-11-07)
| Área | Ítem | Estado | Evidencia |
|---|---|---|---|
| Observabilidad | Alertas por síntoma con runbook | Cumple | docs/runbooks/orders-lag.md |
| Datos | Restore probado | No cumple | riesgo R-014 aceptado hasta 2026-12-15 |
| Resiliencia | Timeouts y circuit breaker | Cumple | ADR-0012, test ResilienceIT |
| Infra | Terraform | Validada estáticamente; preparado para AWS, no verificado en real | CI tf-validate |
Decisión: pendiente de aprobación humana (gate).
```

## Checklist de revisión
- [ ] Cada ítem tiene estado y evidencia enlazada.
- [ ] Los "No cumple" críticos tienen riesgo aceptado con dueño y fecha.
- [ ] La etiqueta de madurez de infra es honesta.
- [ ] Aprobación registrada por una persona, no por el agente.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de afirmaciones honestas sobre AWS | 1 | `factory/validators/honest_claims.py` |
| Gates humanos: no se crean ni editan aprobaciones desde el agente | 2 | `gates/` |
| Aprobación de la PRR | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `risk-register`, `runbooks`, `backup-and-restore`, `alerting-symptom-based`, `change-and-release-management`, `honest-claims-policy`.
- Fuentes: Google SRE Book/Workbook, "Production Readiness Review" (TODO-VERIFY URL concreta).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
