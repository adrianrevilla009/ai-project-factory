---
name: scp-guardrails
description: "Usar al escribir o revisar Service Control Policies de AWS Organizations: denegación de regiones, protección de trails, KMS y root."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# SCP como guardarraíles

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica a SCP adjuntas a OUs/cuentas en Terraform.
- No aplica a permisos de identidad (permission sets, ver `identity-center-sso`). Las SCP no conceden permisos; solo fijan el techo.

## Reglas
- **MUST** usar estrategia "deny list": mantener `FullAWSAccess` y añadir denegaciones concretas.
- **MUST** denegar acciones fuera de eu-west-1 y eu-central-1 (D6) con `aws:RequestedRegion`, exceptuando servicios globales (IAM, Organizations, Route 53, CloudFront, etc.; lista por validar, TODO-VERIFY).
- **MUST** denegar desactivar o borrar CloudTrail, Config, GuardDuty y Security Hub de la organización.
- **MUST** denegar uso del usuario root en cuentas miembro y la creación de access keys.
- **MUST** denegar `kms:ScheduleKeyDeletion` y `kms:DisableKey` salvo rol de plataforma.
- **MUST** probar cada SCP en una OU `Sandbox` antes de adjuntarla a `Workloads`.
- **SHOULD** versionar SCP en ficheros JSON con `Sid` descriptivo y tamaño < límite de 5120 caracteres (TODO-VERIFY).
- **MUST NOT** adjuntar SCP experimentales a la raíz de la organización.
- **MUST NOT** olvidar que las SCP no afectan a la cuenta de management.

## Por qué
Una SCP errónea en la raíz puede dejar a toda la organización sin acceso. El techo preventivo es la última defensa si un permission set es demasiado amplio.

## Ejemplos
### Mal
```json
{ "Effect": "Deny", "Action": "*", "Resource": "*" }
```
### Bien
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "DenyOutsideAllowedRegions",
    "Effect": "Deny",
    "NotAction": ["iam:*", "organizations:*", "route53:*", "cloudfront:*", "support:*", "sts:*"],
    "Resource": "*",
    "Condition": {
      "StringNotEquals": { "aws:RequestedRegion": ["eu-west-1", "eu-central-1"] }
    }
  }]
}
```

## Checklist de revisión
- [ ] Deny list sobre `FullAWSAccess`.
- [ ] Región restringida a eu-west-1/eu-central-1 con excepciones globales.
- [ ] Trails, Config, GuardDuty protegidos.
- [ ] Root y borrado de KMS denegados.
- [ ] Probada primero en Sandbox.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Rego/Conftest: SCP sin `Deny` de región ni protección de trail | 1 | pendiente: `policies/opa-conftest/` |
| Checkov: SCP con `Action: "*"` y `Resource: "*"` en Deny | 1 | pendiente: `policies/iac-checks/` |
| Revisión humana antes de adjuntar a raíz/OU de prod | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `organization-and-ou-design`, `regions-and-data-residency`, `kms-multi-region-keys`, `org-cloudtrail-config-securityhub-guardduty`.
- Fuentes: AWS Organizations User Guide, sección SCP (2026-11-07) — TODO-VERIFY lista de acciones globales y límites.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
