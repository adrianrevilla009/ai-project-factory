---
name: on-call-and-runbook-links
description: "Usar al preparar un servicio para guardia: runbooks enlazados desde alertas y dashboards, rotación, escalado y postmortems sin culpas."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Guardia y enlaces a runbooks

## Cuándo aplicar y cuándo no
- Aplica a cualquier servicio con alertas paginables y a la documentación operativa que las acompaña.
- No aplica a la gestión de incidentes de seguridad (ver `vulnerability-sla-and-incident-response`) ni a herramientas de paginación concretas.

## Reglas
- **MUST** que cada alerta paginable lleve `runbook_url` a un runbook versionado en el repo del servicio (`docs/runbooks/<alert>.md`) o en la wiki oficial.
- **MUST** que el runbook contenga: qué significa la alerta, impacto, comprobaciones iniciales (con enlaces a dashboard y consultas de logs/trazas), mitigaciones seguras, cuándo escalar y a quién.
- **MUST** que las mitigaciones destructivas (borrar datos, reiniciar bases de datos, rollback de esquema) se describan como texto con advertencia y requieran confirmación humana; **MUST NOT** incluir comandos peligrosos listos para pegar sin contexto.
- **MUST** que cada dashboard enlace a su runbook y a los de sus dependencias, y cada servicio tenga un dueño y un canal de escalado definidos.
- **SHOULD** probar los runbooks en ejercicios (game days) y corregirlos tras cada uso.
- **MUST** hacer postmortem sin culpas de cada incidente que consuma presupuesto de error significativo, con acciones con dueño y fecha.
- **SHOULD** limitar la carga de guardia (páginas por turno) y tratar el exceso como deuda de fiabilidad (ver `alerting-symptom-based`).
- **MUST NOT** guardar credenciales ni datos personales en runbooks; referirse al gestor de secretos.

## Por qué
A las 3 a. m. nadie recuerda el contexto: el runbook convierte la alerta en una secuencia de pasos. Si el enlace no existe o está caducado, el tiempo de recuperación se multiplica. Los postmortems sin culpas generan aprendizaje en vez de ocultación.

## Ejemplos
### Mal
```yaml
annotations:
  summary: "orders-api mal"
  description: "Revisar logs y reiniciar si hace falta"
```
### Bien
```yaml
annotations:
  summary: "orders-api: error budget fast burn"
  dashboard: "https://grafana.example.internal/d/orders-api"
  runbook_url: "https://git.example.internal/shop/orders-api/blob/main/docs/runbooks/error-budget-fast-burn.md"
```
```markdown
# Runbook: OrdersApiErrorBudgetFastBurn
Impacto: pedidos fallan para parte de los usuarios.
1. Abrir el dashboard enlazado; confirmar tasa de 5xx por endpoint.
2. Comprobar despliegues recientes (rollback con GitOps si coincide).
3. Revisar saturación del pool de BD y lag de Kafka.
Escalar a: guardia de plataforma tras 15 minutos sin mejora.
Atención: no truncar tablas ni reiniciar la BD sin aprobación humana.
```

## Checklist de revisión
- [ ] Toda alerta `page` tiene `runbook_url` válido.
- [ ] Runbook con impacto, comprobaciones, mitigaciones y escalado.
- [ ] Dueño y canal de escalado definidos.
- [ ] Proceso de postmortem acordado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: alerta `page` sin `runbook_url` o enlace inexistente (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |
| Revisión de runbooks y organización de guardia | 3/4 | agente `code-reviewer` y revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `alerting-symptom-based`, `slo-sli-error-budgets`, `golden-signals-red-use`, `vulnerability-sla-and-incident-response`.
- Fuentes: Google SRE Book (on-call, postmortem culture), consultado 2026-11-07. La fábrica no despliega ni opera: los runbooks son guía para el proyecto generado.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
