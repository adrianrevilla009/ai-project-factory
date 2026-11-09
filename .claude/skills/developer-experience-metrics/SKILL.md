---
name: developer-experience-metrics
description: "Usar al definir métricas de experiencia de desarrollo y entrega (DORA, tiempo de onboarding, encuestas) sin convertirlas en vigilancia individual."
metadata:
  block: "20-internal-developer-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Métricas de experiencia de desarrollo

## Cuándo aplicar y cuándo no
- Aplica al medir si la plataforma interna mejora la entrega: frecuencia de despliegue, lead time, tasa de fallo de cambios, tiempo de recuperación, más señales cualitativas.
- No aplica a evaluar el rendimiento de personas: estas métricas son de sistema y de equipo.

## Reglas
- **MUST** medir a nivel de equipo/servicio, nunca ranking de individuos.
- **MUST** combinar métricas de flujo (las cuatro de DORA) con señales cualitativas (encuesta trimestral corta de satisfacción y fricciones).
- **MUST** definir cada métrica con fórmula, fuente de datos y qué evento cuenta (qué es "despliegue", qué es "fallo").
- **MUST** medir también tiempo hasta el primer despliegue de un desarrollador nuevo y tiempo de creación de un servicio con el golden path.
- **SHOULD** obtener datos de forma automática (Git, CI, GitOps, incidentes), no de hojas manuales.
- **SHOULD** usar tendencias y mediana/percentiles, no medias de un solo dato.
- **MUST NOT** usar una métrica como objetivo contractual (ley de Goodhart): se falsea.
- **MUST NOT** publicar datos de encuestas identificables.

## Por qué
Sin medición, la plataforma se justifica por intuición. Pero métricas mal usadas incentivan trampas (partir despliegues para subir la frecuencia). Las cualitativas detectan fricciones que los números no ven.

## Ejemplos
### Mal
```text
Objetivo de equipo: 10 despliegues por persona y semana.
Ranking de commits por desarrollador en el dashboard.
```
### Bien
```yaml
# platform/metrics/definitions.yaml (esquema ilustrativo)
metrics:
  deployment_frequency:
    scope: service
    source: gitops-sync-events
    counts: sync a producción con éxito
  lead_time_for_changes:
    scope: service
    from: primer commit del PR
    to: despliegue en producción
    aggregate: p50, p90
  change_failure_rate:
    source: incident-tracker
    counts: despliegues que causan rollback o incidente
  time_to_restore:
    source: incident-tracker
  onboarding_time:
    scope: team
    from: alta de cuenta
    to: primer cambio en producción
survey:
  cadence: quarterly
  anonymous: true
```

## Checklist de revisión
- [ ] Cada métrica tiene fórmula, fuente y alcance de equipo.
- [ ] Hay componente cualitativo anónimo.
- [ ] Nada se usa como objetivo individual.
- [ ] Datos recogidos automáticamente.
- [ ] Revisión periódica de la utilidad de cada métrica.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Uso ético de métricas y definición de objetivos | 4 | revisión humana |

No hay mecanismo automático: es una decisión de gestión.

## Relacionados, fuentes y mantenimiento
- Relacionados: `golden-paths-governance`, `backstage`, `finops`.
- Fuentes: DORA, https://dora.dev/.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
