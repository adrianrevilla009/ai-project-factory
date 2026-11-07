---
name: golden-paths-governance
description: "Usar al definir, versionar o retirar golden paths (caminos pavimentados) de la plataforma interna y decidir cuándo una desviación está permitida."
metadata:
  block: "20-internal-developer-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Gobierno de golden paths

## Cuándo aplicar y cuándo no
- Aplica cuando la plataforma ofrece caminos recomendados (plantilla + pipeline + runtime) y hay que decidir qué es obligatorio, qué es opcional y cómo evolucionan.
- No aplica a decisiones de arquitectura de un único servicio (ver ADRs y `evolutionary-architecture-fitness-functions`).

## Reglas
- **MUST** que cada golden path tenga dueño (equipo), versión semántica, changelog y fecha de revisión.
- **MUST** que el camino sea más fácil que la alternativa: si desviarse es más cómodo, el camino ha fallado.
- **MUST** separar lo obligatorio (seguridad, observabilidad, trazabilidad de dueño) de lo recomendado (framework, estructura).
- **MUST** documentar el proceso de desviación: ADR corto con motivo, riesgo, dueño y fecha de caducidad.
- **SHOULD** medir adopción y satisfacción (ver `developer-experience-metrics`) y retirar caminos que nadie usa.
- **SHOULD** anunciar cambios incompatibles con un periodo de migración y herramientas de actualización automática.
- **MUST NOT** convertir el camino en un gate manual: el cumplimiento se comprueba con policies automáticas.
- **MUST NOT** mantener caminos zombis sin dueño.

## Por qué
Un golden path impuesto sin escucha genera shadow IT; uno sin gobierno acumula variantes. La caducidad de las desviaciones evita que las excepciones se vuelvan permanentes sin que nadie las revise.

## Ejemplos
### Mal
```text
Golden path "java-service" v?  - sin dueño, sin changelog.
Excepción concedida por chat: "vale, usa otro logger".
```
### Bien
```yaml
# platform/golden-paths/java-service.yaml
name: java-service
version: 2.3.0
owner: group:default/platform-team
mandatory: [catalog-info, sbom, image-signing, structured-logging]
recommended: [spring-boot-actuator, testcontainers]
deprecation:
  replaces: 2.2.x
  migrate_until: 2027-03-31
exceptions:
  - id: EXC-014
    service: legacy-billing
    reason: logger corporativo heredado
    adr: docs/adr/0042-legacy-logger.md
    expires: 2027-01-31
```
(Esquema ilustrativo, no un formato estándar.)

## Checklist de revisión
- [ ] Dueño, versión y changelog definidos.
- [ ] Obligatorio vs recomendado separados.
- [ ] Excepciones con ADR y fecha de caducidad.
- [ ] Hay métrica de adopción.
- [ ] Plan de migración para versiones incompatibles.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Aprobación de cambios de camino obligatorio y excepciones | 4 | revisión humana |
| Comprobación automática de lo obligatorio | 1 | pendiente (policies en `policies/opa-conftest/` y `policies/kyverno/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `backstage`, `software-templates`, `developer-experience-metrics`, `tech-debt-management`.
- Fuentes: ninguna oficial única; criterio de ingeniería de plataforma. TODO-VERIFY si se cita CNCF Platforms White Paper (https://tag-app-delivery.cncf.io/whitepapers/platforms/).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
