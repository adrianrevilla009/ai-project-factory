---
name: org-cloudtrail-config-securityhub-guardduty
description: "Usar al diseñar la detección y auditoría a nivel organización en AWS: CloudTrail org, AWS Config, Security Hub y GuardDuty con administrador delegado."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# CloudTrail, Config, Security Hub y GuardDuty a nivel organización

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica a la configuración de servicios de auditoría y detección para toda la organización.
- No aplica a observabilidad de aplicación (bloque de observabilidad) ni a Falco/runtime en Kubernetes. En local no se reproduce ninguno de estos servicios.

## Reglas
- **MUST** crear un trail de organización multi-región, con validación de integridad de ficheros, entregado al bucket de `log-archive`.
- **MUST** habilitar AWS Config con agregador en la cuenta `audit` y registrar recursos en eu-west-1 y eu-central-1 (D6).
- **MUST** habilitar GuardDuty y Security Hub con administrador delegado en la cuenta `audit` y auto-enable para cuentas nuevas.
- **MUST** cifrar trail y entregas con CMK (ver `kms-multi-region-keys`).
- **MUST** definir el estándar de Security Hub adoptado (p. ej. AWS Foundational Security Best Practices) y registrar excepciones con caducidad.
- **SHOULD** enrutar hallazgos HIGH/CRITICAL a un canal de alerta con propietario.
- **SHOULD** habilitar data events solo donde aporte (coste); documentar la decisión.
- **MUST NOT** gestionar estos servicios desde la cuenta de management más allá del alta de la delegación.
- **MUST NOT** permitir que una cuenta miembro desactive el trail (SCP, ver `scp-guardrails`).

## Por qué
Sin trail central y agregación, un incidente en una cuenta no es reconstruible. Delegar a `audit` evita usar la cuenta de management, que las SCP no restringen.

## Ejemplos
### Mal
```hcl
resource "aws_cloudtrail" "t" {
  name           = "trail"
  s3_bucket_name = aws_s3_bucket.logs.id   # cuenta local, sin KMS, una región
}
```
### Bien
```hcl
resource "aws_cloudtrail" "org" {
  name                          = "org-trail"
  s3_bucket_name                = var.log_archive_bucket
  is_organization_trail         = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  kms_key_id                    = var.cloudtrail_kms_key_arn
  include_global_service_events = true
}

resource "aws_guardduty_organization_admin_account" "this" {
  admin_account_id = var.audit_account_id
}
```

## Checklist de revisión
- [ ] Trail org multi-región con validación y KMS.
- [ ] Config con agregador en `audit`.
- [ ] GuardDuty y Security Hub con admin delegado y auto-enable.
- [ ] Estándar de Security Hub documentado; excepciones con fecha.
- [ ] Ruta de alertas con propietario.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov: `aws_cloudtrail` con `is_multi_region_trail`, validación y KMS (checks nativos CKV_AWS_35/36/67, IDs verificados en Checkov 3.3.13 el 2026-11-08) | 1 | pendiente: configuración en `policies/iac-checks/` |
| Revisión de excepciones de Security Hub | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `log-archive-and-audit-account`, `scp-guardrails`, `kms-multi-region-keys`, `compliance-as-code`.
- Fuentes: guías de usuario de CloudTrail, Config, Security Hub y GuardDuty (2026-11-07) — comprobar URLs y estándares vigentes.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
