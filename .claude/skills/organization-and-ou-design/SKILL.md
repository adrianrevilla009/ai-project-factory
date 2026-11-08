---
name: organization-and-ou-design
description: "Usar al diseñar la estructura de AWS Organizations (cuentas y OUs) de un proyecto: separación por entorno, carga de trabajo, seguridad y logging."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Diseño de la organización y OUs

Skill de diseño: la fábrica nunca despliega en AWS (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica al definir el árbol de OUs y cuentas en Terraform para un proyecto generado.
- No aplica al entorno local (no hay equivalente de Organizations en local; NO se reproduce) ni a la red (ver bloque 12).

## Reglas
- **MUST** usar cuentas distintas como frontera de aislamiento: una por entorno (`dev`, `staging`, `prod`) y por dominio de carga cuando el blast radius lo justifique.
- **MUST** tener cuentas dedicadas de gestión (management, sin cargas), `log-archive` y `audit` (ver `log-archive-and-audit-account`).
- **MUST** organizar OUs por función de política, no por organigrama: `Security`, `Infrastructure`, `Workloads/Prod`, `Workloads/NonProd`, `Sandbox`, `Suspended`.
- **MUST** parametrizar regiones: eu-west-1 primaria y eu-central-1 secundaria (D6), sin literales en módulos.
- **MUST NOT** ejecutar cargas de trabajo en la cuenta de management.
- **SHOULD** limitar la profundidad de OUs (≤ 3 niveles) para que las SCP sean razonables.
- **SHOULD** usar emails de cuenta como alias de grupo (`aws+prod-orders@example.com`), nunca personales.
- **SHOULD** mover cuentas cerradas a la OU `Suspended` con SCP de denegación total.

## Por qué
La cuenta es la única frontera fuerte de IAM, cuotas y facturación. Un árbol por política permite aplicar SCP a una OU y heredarlas. Mezclar prod y no-prod en una cuenta obliga a depender solo de tags e IAM condicional.

## Ejemplos
### Mal
```hcl
# todo en una cuenta, OU plana por equipo
resource "aws_organizations_organizational_unit" "team_a" {
  name      = "team-a"
  parent_id = data.aws_organizations_organization.this.roots[0].id
}
```
### Bien
```hcl
locals {
  root_id = data.aws_organizations_organization.this.roots[0].id
  ous     = ["Security", "Infrastructure", "Workloads", "Sandbox", "Suspended"]
}

resource "aws_organizations_organizational_unit" "top" {
  for_each  = toset(local.ous)
  name      = each.key
  parent_id = local.root_id
}

resource "aws_organizations_organizational_unit" "prod" {
  name      = "Prod"
  parent_id = aws_organizations_organizational_unit.top["Workloads"].id
}
```

## Checklist de revisión
- [ ] Existe cuenta de management sin cargas, `log-archive` y `audit`.
- [ ] Prod y no-prod en cuentas y OUs separadas.
- [ ] OUs definidas por política, máx. 3 niveles.
- [ ] Regiones por variable (D6), sin literales.
- [ ] Emails de cuenta son alias de grupo.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov custom: `aws_instance`/`aws_eks_cluster` en cuenta de management | 1 | pendiente: `policies/iac-checks/` |
| Revisión de árbol de OUs | 3 | agente de arquitectura / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `control-tower-and-account-factory`, `scp-guardrails`, `log-archive-and-audit-account`, `regions-and-data-residency`.
- Fuentes: AWS Organizations User Guide y whitepaper "Organizing Your AWS Environment Using Multiple Accounts" (2026-11-07) — comprobar URL y límites vigentes.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
