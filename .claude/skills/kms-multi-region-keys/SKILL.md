---
name: kms-multi-region-keys
description: "Usar al diseñar claves AWS KMS: CMK por dominio, claves multi-región entre eu-west-1 y eu-central-1, key policies y rotación."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Claves KMS y multi-región

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica a CMK que cifran S3, EBS, RDS, EKS secrets, trails y backups.
- No aplica al cifrado de aplicación con Vault Transit (bloque de secretos). En local KMS no se reproduce; se simula con Vault OSS o claves de test.

## Reglas
- **MUST** usar CMK gestionadas por el cliente (no claves `aws/*`) para datos sensibles y logs de seguridad.
- **MUST** separar claves por dominio de datos y entorno (`orders-prod-data`, `org-trail`), no una clave global.
- **MUST** activar rotación automática en claves simétricas.
- **MUST** usar claves multi-región (réplica en eu-central-1) solo donde la recuperación entre regiones lo requiera (D6); la réplica comparte material pero tiene key policy propia.
- **MUST** escribir la key policy con mínimo privilegio, separando administradores de usuarios de la clave; sin `"Principal": "*"` sin condición.
- **MUST** denegar `ScheduleKeyDeletion` por SCP y exigir ventana de espera máxima.
- **SHOULD** usar alias (`alias/orders-prod-data`) y nunca ARNs de clave embebidos en código.
- **SHOULD** usar grants o condiciones `kms:ViaService` para acotar el uso.
- **MUST NOT** usar claves multi-región por defecto: amplían el radio de impacto.

## Por qué
Una clave multi-región permite descifrar datos replicados sin recifrar, útil en DR, pero cualquier compromiso afecta a ambas regiones. Mejor decidirlo por caso.

## Ejemplos
### Mal
```hcl
resource "aws_kms_key" "k" {
  policy = jsonencode({ Statement = [{ Effect = "Allow", Principal = "*", Action = "kms:*", Resource = "*" }] })
}
```
### Bien
```hcl
resource "aws_kms_key" "orders_data" {
  description             = "orders-prod data at rest"
  enable_key_rotation     = true
  multi_region            = true
  deletion_window_in_days = 30
  policy                  = data.aws_iam_policy_document.orders_data_key.json
}

resource "aws_kms_replica_key" "orders_data_dr" {
  provider        = aws.secondary # eu-central-1
  primary_key_arn = aws_kms_key.orders_data.arn
  policy          = data.aws_iam_policy_document.orders_data_key.json
}
```

## Checklist de revisión
- [ ] CMK propia por dominio y entorno.
- [ ] `enable_key_rotation = true`.
- [ ] Multi-región justificada por un requisito de DR.
- [ ] Key policy sin comodines abiertos.
- [ ] Alias en vez de ARN literal.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov nativo: rotación KMS (CKV_AWS_7, comprobar id) y política sin comodín (CKV_AWS_33) | 1 | pendiente: configuración en `policies/iac-checks/` |
| Conftest: `multi_region = true` sin comentario de justificación | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de key policies | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `envelope-encryption-and-kms`, `scp-guardrails`, `log-archive-and-audit-account`, `regions-and-data-residency`.
- Fuentes: AWS KMS Developer Guide, multi-Region keys (2026-11-07) — comprobar URL y servicios compatibles.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
