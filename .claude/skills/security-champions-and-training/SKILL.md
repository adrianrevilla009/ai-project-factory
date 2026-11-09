---
name: security-champions-and-training
description: "Usar al montar un programa de security champions y formación de seguridad para equipos de desarrollo, con roles, cadencia y métricas útiles."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Security champions y formación

## Cuándo aplicar y cuándo no
- Aplica al diseñar cómo los equipos de producto incorporan seguridad día a día: personas de referencia, formación, y participación en revisiones.
- No aplica a la formación obligatoria legal genérica (concienciación corporativa) más allá de enlazarla, ni sustituye al equipo de seguridad.

## Reglas
- **MUST** nombrar al menos un champion por equipo de producto, voluntario y con tiempo explícito (p. ej. 10 % del sprint), con respaldo de su responsable.
- **MUST** definir el rol: punto de contacto con seguridad, primer revisor en cambios sensibles, difusión de hallazgos; el champion NO es el único responsable de la seguridad del equipo.
- **MUST** dar formación específica por rol y stack (desarrolladores Java/React, SRE, QA), con ejercicios prácticos sobre vulnerabilidades reales de esa pila.
- **MUST** incluir en el onboarding: gestión de secretos, revisión de dependencias, reporte de incidentes y canal para dudas.
- **MUST** realimentar la formación con datos: los hallazgos recurrentes (SAST, revisiones, incidentes) determinan los temas.
- **SHOULD** reunir a los champions con cadencia regular (mensual o quincenal) y publicar notas.
- **SHOULD** reconocer la labor: objetivos, evaluación de desempeño o visibilidad, no solo trabajo extra.
- **SHOULD** medir con indicadores de resultado: tiempo de corrección, repetición de tipos de vulnerabilidad, participación en revisiones; no solo asistencia a cursos.
- **MUST NOT** usar entornos o datos de producción para ejercicios prácticos; solo laboratorios propios y aislados.
- **MUST NOT** culpar a individuos por errores reportados; el reporte temprano debe ser seguro (cultura sin culpa).

## Por qué
El equipo de seguridad no escala a revisar cada cambio. Distribuir criterio en los equipos acelera la detección y evita cuellos de botella, pero solo funciona si hay tiempo asignado, formación pertinente y métricas que midan resultados en lugar de actividad.

## Ejemplos
### Mal
```text
Curso anual de 1 hora para todos, igual para cualquier rol. "Champion" nombrado por
decreto sin tiempo ni formación; se mide el % de asistentes que aprobó el test.
```
### Bien
```yaml
# champions-program.example.yaml
roles:
  champion: {time_budget: "10% sprint", responsibilities: [first-reviewer, triage-findings, share-lessons]}
cadence:
  sync: biweekly
  workshop: quarterly        # laboratorio aislado con app vulnerable propia
training_topics_source: "top 3 hallazgos SAST y revisiones del trimestre"
onboarding: [secrets-management, dependency-hygiene, incident-reporting]
metrics:
  - mean_time_to_fix_high_findings
  - recurrence_rate_by_vulnerability_class
  - share_of_sensitive_PRs_reviewed_by_champion
safe_reporting: blameless
```

## Checklist de revisión
- [ ] Cada equipo tiene champion con tiempo asignado.
- [ ] La formación es por rol y stack, con práctica.
- [ ] Los temas se derivan de hallazgos reales.
- [ ] Las métricas miden resultados, no solo asistencia.
- [ ] Los ejercicios usan laboratorios aislados.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión del programa contra la checklist | 3 | agente revisor / PR |
| Compromiso de tiempo y reconocimiento | 4 | revisión humana (dirección) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `secure-sdlc-nist-ssdf`, `owasp-top10-and-api-top10`, `asvs-mapping`, `incident-management-and-postmortems`, `code-review-guidelines`, `threat-modeling-stride`.
- Fuentes: OWASP Security Champions Guide y SAMM; NIST SSDF (SP 800-218) para prácticas de formación.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
