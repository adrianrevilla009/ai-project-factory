---
name: pipeline-observability-and-dora
description: "Usar al medir el pipeline: métricas DORA, duración, tasa de fallos y flakiness, y cómo emitirlas sin datos sensibles."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Observabilidad del pipeline y métricas DORA

## Cuándo aplicar y cuándo no
- Aplica a equipos que quieren medir y mejorar el flujo de entrega.
- No aplica a la observabilidad de los servicios en ejecución (bloque 18).
- Las métricas son para mejorar el sistema, no para evaluar a personas.

## Reglas
- **MUST** capturar las cuatro métricas DORA: frecuencia de despliegue, lead time de cambios, tasa de fallo de cambios y tiempo de recuperación (MTTR). Definiciones por proyecto, escritas en el repo.
- **MUST** emitir un evento por despliegue (servicio, versión/digest, entorno, resultado, timestamp, SHA) desde el propio pipeline, incluidos los rollbacks.
- **MUST** definir "fallo de cambio" (rollback, hotfix o incidencia atribuida a un despliegue) y enlazarlo a la gestión de incidentes (`incident-management-and-postmortems`).
- **SHOULD** medir además duración por etapa, tiempo en cola de runners, tasa de reintentos y tests inestables (flakiness).
- **SHOULD** exportar a la plataforma de observabilidad (OpenTelemetry/Prometheus) y mostrar en un dashboard como código.
- **MUST NOT** incluir secretos, datos personales ni nombres de personas en eventos o métricas.
- **MUST NOT** usar las métricas DORA como objetivo individual o ranking de equipos (ley de Goodhart).

## Por qué
Sin eventos de despliegue no hay lead time ni tasa de fallo fiables. Medir etapas revela dónde se pierde tiempo (colas, tests lentos) antes de optimizar a ciegas.

## Ejemplos
### Mal
```text
DORA calculado a mano en una hoja cada trimestre; "fallo" = lo que recuerde el equipo
```
### Bien
```yaml
- name: emit deployment event
  if: always()
  run: |
    jq -n --arg svc orders --arg env "$ENV" --arg sha "$GITHUB_SHA" \
          --arg digest "$IMAGE_DIGEST" --arg result "${{ job.status }}" \
          '{service:$svc, environment:$env, sha:$sha, digest:$digest, result:$result, ts:(now|todate)}' \
      | curl -fsS -X POST -H 'Content-Type: application/json' -d @- "$DEPLOY_EVENTS_URL"
```
`DEPLOY_EVENTS_URL` es un endpoint interno del proyecto (por definir). Lead time = tiempo entre el primer commit del cambio y el evento de despliegue exitoso en producción.

## Checklist de revisión
- [ ] Evento de despliegue emitido en éxito, fallo y rollback.
- [ ] "Fallo de cambio" definido y enlazado a incidentes.
- [ ] Dashboard versionado como código.
- [ ] Sin datos sensibles en los eventos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Rego: workflow de CD incluye paso de evento de despliegue | 1 | pendiente |
| Revisión de definiciones y uso de las métricas | 3 | agente `code-reviewer` / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rollback-strategy`, `dashboards-and-slos-as-code`, `incident-management-and-postmortems`, `change-and-release-management`.
- Fuentes: DORA (https://dora.dev/guides/dora-metrics/) — comprobar nombres actuales de las métricas (la guía puede haber renombrado "fallo de cambio" y "MTTR").
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
