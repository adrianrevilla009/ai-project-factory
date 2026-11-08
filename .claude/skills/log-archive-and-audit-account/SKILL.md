---
name: log-archive-and-audit-account
description: "Usar al diseñar las cuentas log-archive y audit de AWS: buckets inmutables de logs, retención, replicación entre regiones y acceso de solo lectura."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Cuentas log-archive y audit

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica a buckets y roles que almacenan logs de seguridad de la organización.
- No aplica a logs de aplicación (observabilidad) ni a logs de Kubernetes. En local solo se emula con almacenamiento S3 compatible sin garantías de inmutabilidad.

## Reglas
- **MUST** separar `log-archive` (solo almacenamiento) de `audit` (herramientas de seguridad y consulta de solo lectura).
- **MUST** activar en los buckets: versionado, Block Public Access, cifrado SSE-KMS y S3 Object Lock en modo compliance o governance según política (comprobar requisitos legales).
- **MUST** definir retención explícita (p. ej. 365 días en caliente y archivado después; plazo legal por confirmar con fuente oficial) con lifecycle.
- **MUST** replicar a un bucket en eu-central-1 (secundaria, D6) si el log es evidencia.
- **MUST** restringir con política de bucket: escritura solo desde servicios de la organización (`aws:PrincipalOrgID`), borrado denegado.
- **SHOULD** dar a `audit` acceso de lectura mediante rol, nunca claves.
- **MUST NOT** permitir a roles de workload leer el bucket de logs de seguridad.
- **MUST NOT** guardar datos personales en claro en logs.

## Por qué
Un atacante con privilegios en una cuenta intenta borrar sus huellas; si los logs viven en esa cuenta, lo consigue. Aislarlos con Object Lock y política de organización preserva la evidencia.

## Ejemplos
### Mal
```hcl
resource "aws_s3_bucket" "logs" { bucket = "my-logs" }  # sin versionado, sin lock, sin KMS
```
### Bien
```hcl
resource "aws_s3_bucket" "org_logs" {
  bucket              = "example-org-log-archive-euw1"
  object_lock_enabled = true
}

resource "aws_s3_bucket_versioning" "org_logs" {
  bucket = aws_s3_bucket.org_logs.id
  versioning_configuration { status = "Enabled" }
}

resource "aws_s3_bucket_public_access_block" "org_logs" {
  bucket                  = aws_s3_bucket.org_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

## Checklist de revisión
- [ ] `log-archive` y `audit` son cuentas distintas.
- [ ] Versionado, BPA, KMS y Object Lock activos.
- [ ] Retención y lifecycle definidos; plazo legal marcado por confirmar.
- [ ] Réplica a eu-central-1 si es evidencia.
- [ ] Política de bucket por `aws:PrincipalOrgID`, sin borrado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov: S3 sin versionado/BPA/KMS (checks nativos; los IDs de Checkov usados en estas skills se verificaron con Checkov 3.3.13 el 2026-11-08) | 1 | pendiente: `policies/iac-checks/` |
| Conftest: bucket de logs sin `object_lock_enabled` | 1 | pendiente: `policies/opa-conftest/` |
| Plazos de retención | 4 | revisión humana (normativa por confirmar) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `org-cloudtrail-config-securityhub-guardduty`, `kms-multi-region-keys`, `regions-and-data-residency`.
- Fuentes: S3 User Guide (Object Lock) y CloudTrail User Guide (2026-11-07) — comprobar URLs; retención legal: borrador por confirmar.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
