---
name: quality-attributes-atam
description: Usar al definir atributos de calidad medibles y evaluar compromisos arquitectónicos (ATAM) antes de fijar una arquitectura.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Atributos de calidad y ATAM

## Cuándo aplicar y cuándo no
- Aplica al iniciar una arquitectura, antes de decisiones caras de revertir (datos, comunicación, despliegue) y al revisar una existente.
- No aplica a cambios locales sin impacto arquitectónico. ATAM completo solo para sistemas críticos; para el resto, versión ligera.

## Reglas
- **MUST** expresar cada atributo de calidad relevante como escenario medible: estímulo, entorno, respuesta y medida (p95 < 300 ms al 70 % de carga).
- **MUST** priorizar los escenarios (impacto de negocio x dificultad) y limitarse a los 3-5 que condicionan la arquitectura.
- **MUST** documentar los puntos de sensibilidad, los compromisos (trade-offs) y los riesgos de cada decisión en un ADR.
- **MUST** vincular cada escenario crítico con una verificación: prueba de carga, fitness function o prueba de resiliencia.
- **SHOULD** involucrar a negocio, operaciones y seguridad en la priorización.
- **MUST NOT** declarar atributos sin cifra ("rápido", "escalable", "seguro").
- **MUST NOT** afirmar cumplimiento de disponibilidad en AWS sin medición real: "preparado para AWS, no verificado en real".
- **SHOULD** revisar los escenarios cuando cambie el contexto.

## Por qué
Los atributos de calidad entran en conflicto (latencia vs. consistencia, coste vs. disponibilidad). Sin escenarios medibles, la arquitectura se decide por gusto. ATAM obliga a explicitar compromisos y riesgos antes de que sean caros.

## Ejemplos
### Mal
```text
Requisitos no funcionales: el sistema debe ser rápido, escalable y muy seguro.
```
### Bien
```yaml
# quality-scenarios.yaml
- id: QA-01
  attribute: performance
  stimulus: "1 200 peticiones/s de consulta de catálogo"
  environment: "operación normal"
  response: "responde con datos de caché cuando aplica"
  measure: "p95 <= 200 ms; error rate < 0.1 %"
  verification: "prueba de carga JMeter + fitness function en CI"
  priority: high
- id: QA-02
  attribute: availability
  stimulus: "caída de una instancia de base de datos"
  measure: "RTO <= 15 min, RPO <= 5 min (por confirmar con negocio)"
  verification: "prueba de resiliencia (bloque 08)"
```

## Checklist de revisión
- [ ] Los escenarios tienen estímulo, respuesta y medida.
- [ ] Hay 3-5 escenarios priorizados.
- [ ] Cada decisión registra trade-offs y riesgos.
- [ ] Cada escenario crítico tiene verificación asociada.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión humana de escenarios y ADR; validación de esquema de `quality-scenarios.yaml` pendiente | 4 | ADR del proyecto generado |

## Relacionados, fuentes y mantenimiento
- Relacionados: `evolutionary-architecture-fitness-functions`, `scalability-patterns`, `consistency-and-cap-tradeoffs`, `performance-testing`, `resilience-testing`.
- Fuentes: SEI/CMU, "ATAM: Method for Architecture Evaluation" (2000); Bass, Clements, Kazman, "Software Architecture in Practice".
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
