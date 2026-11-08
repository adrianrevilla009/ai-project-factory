---
name: secure-sdlc-nist-ssdf
description: "Usar al definir o revisar el ciclo de desarrollo seguro de un proyecto y su trazabilidad con NIST SSDF (SP 800-218): prácticas, evidencias y gates por fase."
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "gate"
---

# Secure SDLC alineado con NIST SSDF

## Cuándo aplicar y cuándo no
- Aplica al planificar un proyecto generado, al definir gates de fase y al preparar evidencias de seguridad.
- No aplica como lista de controles técnicos concretos (ver `asvs-mapping`, `dependency-security`) ni como certificación: es una guía de alineamiento, no una afirmación de cumplimiento.

## Reglas
- **MUST** mapear cada fase (requisitos, diseño, implementación, verificación, entrega, operación) a los cuatro grupos SSDF: PO (preparar la organización), PS (proteger el software), PW (producir software bien asegurado), RV (responder a vulnerabilidades).
- **MUST** producir una evidencia verificable por práctica aplicada (fichero, informe de CI, ADR); sin evidencia la práctica cuenta como no cumplida.
- **MUST** exigir modelo de amenazas (`threat-modeling-stride`) antes de la fase de implementación en servicios que expongan API o traten datos personales.
- **MUST** ejecutar en CI análisis estático, de dependencias y de secretos (`security-testing-sast-dast`, `dependency-security`, `secrets-management`).
- **MUST** definir un canal de reporte de vulnerabilidades y un SLA (`vulnerability-sla-and-incident-response`).
- **SHOULD** registrar las excepciones de seguridad como ADR con caducidad y dueño.
- **MUST NOT** declarar "conforme con SSDF" o "certificado"; usar "alineado con SSDF, evidencias en `docs/security/`".

## Por qué
SSDF describe resultados, no herramientas: obliga a poder demostrar qué se hizo y cuándo. Sin tabla de trazabilidad los controles se aplican de forma desigual y no sobreviven a una auditoría. La numeración exacta de prácticas debe contrastarse con el documento vigente (comprobar versión de SP 800-218 y si aplica la revisión 1.2 en borrador).

## Ejemplos
### Mal
```markdown
## Seguridad
Cumplimos NIST SSDF.
```
### Bien
```markdown
## Trazabilidad SSDF (docs/security/ssdf-traceability.md)
| Grupo | Práctica | Evidencia | Fase | Estado |
|---|---|---|---|---|
| PW | Revisar el diseño frente a requisitos de seguridad | docs/security/threat-model-orders.md | Diseño | hecho |
| PW | Análisis estático del código | job `sast` en CI (informe SARIF) | Implementación | hecho |
| PS | Proteger la integridad del código | rama protegida + revisión obligatoria | Implementación | pendiente |
| RV | Gestionar vulnerabilidades | SECURITY.md + SLA | Operación | hecho |
```

## Checklist de revisión
- [ ] Existe tabla de trazabilidad con una evidencia por fila.
- [ ] Hay modelo de amenazas previo a implementar.
- [ ] CI incluye SAST, escaneo de dependencias y de secretos.
- [ ] Existe `SECURITY.md` con canal y SLA.
- [ ] Las excepciones están en ADRs con caducidad.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Gate humano de fase: revisar tabla de trazabilidad | 3 | `gates/` (protocolo `gate-protocol`) |
| Validador que exija `docs/security/ssdf-traceability.md` en el proyecto generado | 2 | pendiente |
| Revisión humana de excepciones | 4 | revisión humana (factory-owner) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `asvs-mapping`, `threat-modeling-stride`, `supply-chain`, `vulnerability-sla-and-incident-response`, `gate-protocol`.
- Fuentes: NIST SP 800-218 (SSDF), csrc.nist.gov — consultada 2026-11-07 solo a nivel de estructura de grupos; comprobar numeración de prácticas.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
