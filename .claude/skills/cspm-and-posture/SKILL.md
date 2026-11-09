---
name: cspm-and-posture
description: "Usar al montar o revisar la vigilancia de postura de seguridad cloud y Kubernetes (CSPM) con herramientas abiertas como Prowler y Kubescape, y su gestión de hallazgos."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# CSPM y postura de seguridad

## Cuándo aplicar y cuándo no
- Aplica al definir cómo se detectan configuraciones inseguras en cuentas cloud y clústeres, y quién las corrige.
- No aplica al escaneo de IaC antes del despliegue (ver `static-verification-ladder`) ni a la seguridad de runtime (ver `runtime-security`).

## Reglas
- **MUST** escanear tanto el código (IaC/manifiestos, en CI) como el estado vivo (cuentas y clústeres, periódicamente): el segundo detecta deriva y cambios manuales.
- **MUST** usar herramientas con licencia abierta por defecto: Prowler (cloud, Apache-2.0) y Kubescape (Kubernetes, Apache-2.0); documentar cualquier alternativa de pago como excepción.
- **MUST** mapear cada hallazgo a un framework de referencia (CIS Benchmark, NSA-CISA, MITRE ATT&CK) para priorizar y dar evidencia.
- **MUST** asignar a cada hallazgo propietario, severidad y SLA de corrección (ver `vulnerability-sla-and-incident-response`).
- **MUST** gestionar excepciones con caducidad, justificación y aprobador; una excepción sin fecha es un hallazgo ignorado.
- **SHOULD** ejecutar el escaneo con credenciales de solo lectura dedicadas, nunca con administrador.
- **SHOULD** medir tendencia (hallazgos abiertos por severidad y antigüedad), no solo el recuento puntual.
- **MUST NOT** almacenar informes con identificadores de cuenta o secretos en repositorios públicos.
- **MUST NOT** declarar "cumple CIS" a partir de un escaneo parcial; indicar versión del benchmark y alcance.

## Por qué
Una configuración correcta el día del despliegue deja de serlo con el primer cambio manual. CSPM convierte la postura en una medición continua con dueño y plazo; sin SLA y excepciones controladas, los informes se acumulan sin acción.

## Ejemplos
### Mal
```text
Se ejecutó Prowler una vez antes de la auditoría, informe en PDF en el correo,
sin propietarios ni fecha de reescaneo.
```
### Bien
```bash
# Comandos de ejemplo (solo lectura; el proyecto generado los ejecuta en su CI/cron)
prowler aws --list-compliance          # ver frameworks disponibles
prowler aws --compliance cis_<version>_aws
kubescape scan framework nsa           # postura del clúster contra NSA-CISA
kubescape scan ./k8s/                  # manifiestos antes de aplicar
```
```yaml
# posture-exception.example.yaml
finding: "s3 bucket without access logging"
owner: platform-team
justification: "bucket temporal de migración"
expires: "2026-12-31"
approved_by: security-lead
```

## Checklist de revisión
- [ ] Hay escaneo en CI y escaneo periódico del estado vivo.
- [ ] Cada hallazgo tiene propietario, severidad y SLA.
- [ ] Las excepciones caducan y tienen aprobador.
- [ ] El informe indica framework, versión y alcance.
- [ ] El escáner usa credenciales de solo lectura.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checks IaC estáticos (Checkov custom) | 1 | `policies/iac-checks/` (pendiente de reglas concretas) |
| Revisión de excepciones y tendencia | 4 | revisión humana periódica |

## Relacionados, fuentes y mantenimiento
- Relacionados: `org-cloudtrail-config-securityhub-guardduty`, `static-verification-ladder`, `container-and-k8s-security`, `compliance-as-code`, `drift-and-self-heal-policy`.
- Fuentes (verificadas 2026-11-07): https://github.com/prowler-cloud/prowler (Apache-2.0, `prowler <provider>`, `--list-compliance`); https://github.com/kubescape/kubescape (Apache-2.0, CNCF incubating, `kubescape scan`, frameworks NSA/MITRE/CIS). Nombres exactos de frameworks.
- Cloud: preparado para AWS, no verificado en real; la fábrica nunca despliega ni escanea cuentas reales (ADR-0004). En local solo Kubescape sobre el clúster local; no se reproduce Security Hub.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
