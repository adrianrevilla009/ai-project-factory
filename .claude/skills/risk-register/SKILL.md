---
name: risk-register
description: "Usar al identificar, puntuar y dar seguimiento a riesgos de proyecto o técnicos: registro versionado con dueño, mitigación y revisión periódica."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Registro de riesgos

## Cuándo aplicar y cuándo no
- Aplica a riesgos de entrega, técnicos, de seguridad, operativos y de dependencia identificados durante un proyecto.
- No aplica a defectos ya ocurridos (son incidencias) ni a deuda conocida sin incertidumbre (ver `tech-debt-register`).

## Reglas
- **MUST** mantener un único registro versionado en el repo (`docs/risks/risk-register.md` o YAML) y revisarlo en cada hito.
- **MUST** que cada riesgo tenga id estable, descripción causa-evento-consecuencia, probabilidad, impacto, dueño nominal, respuesta (evitar, mitigar, transferir, aceptar) y fecha de revisión.
- **MUST** que aceptar un riesgo alto sea una decisión humana registrada con fecha de caducidad.
- **MUST** vincular los riesgos con ADRs, PRR y gates cuando condicionen una decisión.
- **SHOULD** usar escala simple (1-3 o 1-5) y puntuación = probabilidad x impacto, definida una vez.
- **SHOULD** cerrar riesgos con motivo (materializado, mitigado, obsoleto), sin borrarlos.
- **MUST NOT** dejar riesgos sin dueño ni fecha de revisión.
- **MUST NOT** registrar secretos ni datos personales.

## Por qué
Un riesgo visible se gestiona; uno implícito se descubre en producción. El registro también deja constancia de quién aceptó qué y hasta cuándo, útil para auditoría. Los marcos normativos concretos (p. ej. ISO 31000) son borrador por confirmar con fuente oficial.

## Ejemplos
### Mal
```markdown
- Puede fallar Kafka
```
### Bien
```yaml
- id: R-014
  title: Restore de Postgres no probado
  description: "Si no se prueba el restore, una corrupción de datos podría dejar el servicio sin recuperación en RTO."
  probability: 2   # 1-3
  impact: 3
  score: 6
  owner: "tech-lead-orders"
  response: mitigate
  mitigation: "Simulacro de restore en staging"
  accepted_until: "2026-12-15"
  review_date: "2026-12-01"
  status: open
```

## Criterios de decisión y trampas
### Cómo decidir
- Un registro vivo con riesgo, probabilidad, impacto, tratamiento, dueño y fecha de revisión; los riesgos aceptados lo son por una persona con autoridad.
- Revisión periódica.
### Trampas frecuentes
- Un registro que se rellena y se olvida.
- Riesgos sin dueño.
- Aceptar sin decisión explícita.
- Puntuaciones sin criterio.
- Mezclar riesgos con tareas pendientes.
### Evidencia
- Cada riesgo abierto tiene dueño, tratamiento y fecha de revisión.

## Checklist de revisión
- [ ] Cada riesgo tiene dueño, puntuación y fecha de revisión.
- [ ] Los riesgos aceptados tienen aprobación humana y caducidad.
- [ ] Ningún riesgo caducado sigue "aceptado".
- [ ] Los riesgos críticos aparecen en la PRR y los ADRs relacionados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validación de esquema del registro YAML (campos obligatorios, fechas) | 1 | pendiente: esquema JSON en `factory/` del proyecto |
| Revisión periódica en hitos y retros | 4 | revisión humana |

> Estado: el esquema está pendiente.

## Relacionados, fuentes y mantenimiento
- Relacionados: `production-readiness-review`, `tech-debt-register`, `adr`, `lessons-learned-and-retro`.
- Fuentes: ISO 31000 (borrador por confirmar con fuente oficial); sin otra fuente externa.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
