---
name: runbooks
description: "Usar al escribir o revisar runbooks operativos: estructura, verificación, pasos seguros y enlace desde alertas."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Runbooks

## Cuándo aplicar y cuándo no
- Aplica a toda alerta accionable, procedimiento de recuperación, rotación o tarea operativa repetible.
- No aplica a explicaciones de arquitectura (ver `c4-and-arc42`) ni a guiones de DR por región (ver `failover-and-failback-runbooks`).

## Reglas
- **MUST** un runbook por alerta que pagina; la alerta lleva la anotación `runbook_url`.
- **MUST** estructura fija: síntoma, impacto, diagnóstico (comandos de solo lectura primero), mitigación, verificación de que se resolvió, escalado, enlaces.
- **MUST** indicar para cada paso destructivo o irreversible una confirmación explícita y cómo deshacerlo.
- **MUST** indicar dueño, fecha de última ejecución/prueba y entorno al que aplica.
- **SHOULD** probar el runbook en un simulacro (game day, ver `dr-tabletop-exercises`) al menos una vez por año.
- **SHOULD** enlazar los dashboards y consultas exactas, no "mirar métricas".
- **MUST NOT** incluir secretos; referenciar el gestor de secretos.
- **MUST NOT** afirmar que un procedimiento de AWS está verificado: la fábrica no despliega; marcar "preparado para AWS, no verificado en real".

## Por qué
A las 3 de la madrugada nadie recuerda el contexto. Un runbook corto, ejecutable y probado reduce el tiempo de mitigación y el riesgo de empeorar el incidente.

## Ejemplos
### Mal
```markdown
# Kafka lag alto
Revisar Kafka y reiniciar lo que haga falta.
```
### Bien
```markdown
# Alerta: OrdersConsumerLagHigh
Dueño: orders · Última prueba: 2026-09-12 · Entorno: staging, prod

## Impacto
Pedidos tardan en confirmarse; no hay pérdida de datos.

## Diagnóstico (solo lectura)
    kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP --describe --group orders-consumer

## Mitigación
1. Si hay un único pod con errores: `kubectl rollout restart deployment/orders-consumer -n orders`.
2. Si persiste: escalar réplicas (máx. = nº de particiones).

## Verificación
Lag < 1000 durante 10 min en el dashboard "Orders / Consumers".

## Escalado
Tras 30 min sin mejora: guardia de plataforma.
```

## Checklist de revisión
- [ ] Cada alerta que pagina enlaza su runbook.
- [ ] Diagnóstico de solo lectura antes de mitigar.
- [ ] Pasos destructivos con confirmación y reversión.
- [ ] Hay verificación de resolución y vía de escalado.
- [ ] Fecha de última prueba reciente.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Toda regla de alerta con severidad `page` debe tener `runbook_url` | 1 | pendiente: regla Rego en `policies/opa-conftest/` |
| Comprobación de enlaces de `runbook_url` en CI | 1 | pendiente |
| Revisión humana del contenido y simulacros | 3 | revisión humana |

> Estado: ambas comprobaciones automáticas están pendientes.

## Relacionados, fuentes y mantenimiento
- Relacionados: `on-call-and-runbook-links`, `alert-routing-and-oncall`, `failover-and-failback-runbooks`, `dr-tabletop-exercises`, `lessons-learned-and-retro`.
- Fuentes: práctica interna; Google SRE Book, cap. "Being On-Call".
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
