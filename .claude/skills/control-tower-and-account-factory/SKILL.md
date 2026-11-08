---
name: control-tower-and-account-factory
description: "Usar al decidir cómo crear y gobernar cuentas AWS nuevas: Control Tower, Account Factory (AFT) o Terraform propio, y landing zone en eu-west-1."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Control Tower y fábrica de cuentas

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica al diseñar el alta de cuentas, la landing zone y los controles preventivos/detectivos.
- No aplica a la red de las cuentas (bloque 12) ni a diseño de OUs (ver `organization-and-ou-design`).

## Reglas
- **MUST** decidir y registrar en un ADR del proyecto: Control Tower + Account Factory for Terraform (AFT), o Organizations + Terraform propio. Ambos son válidos.
- **MUST** que el alta de cuenta sea código revisado (PR), nunca consola.
- **MUST** fijar la home region de la landing zone en eu-west-1 y gobernar eu-central-1 como región secundaria (D6); la home region no se puede cambiar después sin rehacer la landing zone (comprobar al fijar la versión).
- **MUST** aplicar una línea base a toda cuenta nueva: CloudTrail org, Config, roles de acceso vía Identity Center, tags obligatorios y presupuesto.
- **SHOULD** versionar la personalización de cuentas (baseline) como módulo Terraform con tests estáticos.
- **SHOULD** mantener la lista de regiones gobernadas explícita, no "todas".
- **MUST NOT** crear usuarios IAM de larga duración como parte del alta.
- **MUST NOT** asumir que Control Tower existe en local: no se reproduce; los equivalentes locales son solo contratos de módulo.

## Por qué
Sin fábrica de cuentas, cada cuenta nace distinta y la deriva aparece el primer día. Control Tower acelera la línea base pero acopla a su ciclo de versiones; Terraform propio da control a costa de mantenimiento. La decisión debe ser explícita.

## Ejemplos
### Mal
```text
Alta manual en consola, usuario IAM "admin-temp" con access key, sin tags ni presupuesto.
```
### Bien
```hcl
module "account_orders_prod" {
  source = "./modules/account-baseline"

  account_name  = "orders-prod"
  account_email = "aws+orders-prod@example.com"
  ou_id         = aws_organizations_organizational_unit.prod.id
  home_region   = var.primary_region    # eu-west-1
  dr_region     = var.secondary_region  # eu-central-1
  tags          = local.mandatory_tags
  monthly_budget_eur = 2000
}
```

## Checklist de revisión
- [ ] ADR de Control Tower vs Terraform propio existe.
- [ ] Alta de cuenta solo por PR.
- [ ] Línea base completa (trail, config, SSO, tags, budget).
- [ ] Sin usuarios IAM de larga duración.
- [ ] Home region y regiones gobernadas parametrizadas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov custom: `aws_iam_user`/`aws_iam_access_key` prohibidos | 1 | pendiente: `policies/iac-checks/` |
| Revisión del módulo `account-baseline` | 3 | agente de arquitectura |

## Relacionados, fuentes y mantenimiento
- Relacionados: `organization-and-ou-design`, `identity-center-sso`, `scp-guardrails`, `tagging-cost-allocation-budgets`.
- Fuentes: AWS Control Tower User Guide y repositorio oficial de AFT (2026-11-07) — comprobar versiones y limitaciones de región.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
