---
name: threat-intel-and-risk-register
description: "Usar al incorporar inteligencia de amenazas (CISA KEV, avisos de proveedores) y al mantener el registro de riesgos de seguridad con propietarios, tratamiento y revisión."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Inteligencia de amenazas y registro de riesgos

## Cuándo aplicar y cuándo no
- Aplica a decidir qué fuentes de amenazas se siguen, cómo se convierten en acciones y cómo se registran y tratan los riesgos de seguridad.
- No aplica al modelado de amenazas de un diseño concreto (ver `threat-modeling-stride`) ni a la priorización de CVE individuales (ver `vulnerability-sla-and-incident-response`).

## Reglas
- **MUST** elegir un conjunto pequeño de fuentes relevantes para la pila (avisos de proveedores, catálogo CISA KEV de vulnerabilidades explotadas, avisos del CERT nacional) y asignar un responsable de triarlas.
- **MUST** convertir inteligencia en acción concreta: cada aviso relevante genera una tarea (parchear, regla de detección, bloqueo) o se descarta con motivo anotado.
- **MUST** mantener un registro de riesgos único con: descripción, activo, probabilidad, impacto, propietario de negocio, tratamiento (mitigar, aceptar, transferir, evitar), fecha de revisión.
- **MUST** que un riesgo aceptado lo apruebe quien responde del negocio afectado, con fecha de caducidad.
- **MUST** revisar el registro al menos trimestralmente y tras cada incidente significativo.
- **SHOULD** usar escalas coherentes y documentadas (p. ej. 1-5) y la misma metodología en todo el registro.
- **SHOULD** vincular cada riesgo a controles y a evidencias (hallazgos CSPM, resultados de pruebas).
- **MUST NOT** tratar indicadores de compromiso de fuentes no verificadas como verdad: se validan antes de bloquear.
- **MUST NOT** incluir secretos ni datos personales en el registro de riesgos.

## Por qué
Sin filtro, la inteligencia de amenazas es ruido; sin registro, los riesgos viven en la cabeza de alguien y se aceptan por omisión. El registro hace visibles las decisiones y obliga a que las acepte quien tiene autoridad.

## Ejemplos
### Mal
```text
Riesgos en un Excel personal. "Riesgo: hackers". Sin propietario, sin fecha, sin tratamiento.
Se bloquean IPs de un tuit sin validarlas y se corta un proveedor legítimo.
```
### Bien
```yaml
# risk-register.example.yaml
- id: R-014
  title: "Cuenta de servicio de CI con permisos amplios en el registro de artefactos"
  asset: artifact-registry
  likelihood: 3        # escala 1-5 definida en risk-method.md
  impact: 4
  owner: head-of-engineering
  treatment: mitigate
  controls: [scoped-ci-credentials, audit-alerts]
  evidence: "cspm finding F-221"
  review_by: "2027-02-01"
  status: open
```
```text
Triage semanal: CISA KEV -> ¿usamos el producto? -> sí: ticket con SLA ; no: anotar "no aplica".
```

## Checklist de revisión
- [ ] Fuentes definidas y con responsable de triaje.
- [ ] Todo riesgo tiene propietario de negocio, tratamiento y fecha de revisión.
- [ ] Riesgos aceptados con aprobador y caducidad.
- [ ] Metodología de puntuación documentada.
- [ ] Sin secretos ni datos personales en el registro.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión del registro contra la checklist | 3 | agente revisor / PR |
| Decisiones de aceptación de riesgo | 4 | revisión humana |
| Esquema validable del registro | 1 | pendiente (no existe artefacto aún) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `threat-modeling-stride`, `vulnerability-sla-and-incident-response`, `cspm-and-posture`, `third-party-risk`, `compliance-as-code`.
- Fuentes: catálogo CISA KEV (https://www.cisa.gov/known-exploited-vulnerabilities-catalog); NIST SP 800-30 y ISO/IEC 27005 para metodología de riesgo.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
