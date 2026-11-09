---
name: tagging-cost-allocation-budgets
description: "Usar al definir tags obligatorios, asignación de costes y AWS Budgets en cuentas AWS; también al revisar Terraform sin default_tags."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Tagging, asignación de costes y presupuestos

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica a todo recurso Terraform en AWS y a la línea base de cada cuenta.
- No aplica a labels de Kubernetes (ver OpenCost en el bloque 13), aunque conviene alinear claves.

## Reglas
- **MUST** definir un conjunto mínimo de tags: `project`, `environment`, `owner`, `cost-center`, `data-classification`.
- **MUST** aplicarlos con `default_tags` del provider, no recurso a recurso.
- **MUST** activar los tags como cost allocation tags en la cuenta de facturación (la activación no es retroactiva).
- **MUST** crear un AWS Budget por cuenta con avisos al 50/80/100 % y al previsto, con destinatario real (alias de grupo).
- **SHOULD** usar un tag policy de Organizations para fijar claves y valores permitidos.
- **SHOULD** añadir detección de anomalías de coste.
- **MUST NOT** meter datos personales ni secretos en tags.
- **MUST NOT** depender de tags para autorización sin entender que son editables (usar ABAC solo con control de `TagResource`).

## Por qué
Sin tags no hay chargeback ni forma de saber quién es dueño de un recurso huérfano. Los presupuestos convierten una factura sorpresa en un aviso temprano.

## Ejemplos
### Mal
```hcl
provider "aws" { region = "eu-west-1" }
resource "aws_s3_bucket" "b" { bucket = "example-b" } # sin tags
```
### Bien
```hcl
provider "aws" {
  region = var.primary_region # eu-west-1
  default_tags {
    tags = {
      project             = var.project
      environment         = var.environment
      owner               = "team-orders"
      cost-center         = var.cost_center
      data-classification = "internal"
    }
  }
}

resource "aws_budgets_budget" "monthly" {
  name         = "orders-prod-monthly"
  budget_type  = "COST"
  limit_amount = "2000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "ACTUAL"
    subscriber_email_addresses = ["finops@example.com"]
  }
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Un conjunto pequeño de etiquetas obligatorias (propietario, entorno, producto, coste) impuestas por código y por política, activadas para la asignación de costes.
- Presupuestos con alertas por propietario.
### Trampas frecuentes
- Docenas de etiquetas opcionales.
- Etiquetar a mano.
- Recursos sin dueño.
- Etiquetas que difieren en mayúsculas o nombres.
- Presupuestos sin alertas ni responsable.
### Evidencia
- Un informe de recursos sin etiquetas obligatorias que tiende a cero.

## Checklist de revisión
- [ ] `default_tags` en todos los providers (incluido el secundario).
- [ ] Tags activados para costes.
- [ ] Budget por cuenta con alertas.
- [ ] Sin datos sensibles en tags.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest sobre plan: recurso sin tags obligatorios | 1 | pendiente: `policies/opa-conftest/` |
| Checkov custom: provider sin `default_tags` | 1 | pendiente: `policies/iac-checks/` |
| Revisión FinOps de presupuestos | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `control-tower-and-account-factory`, `compliance-as-code`, `cost-visibility`.
- Fuentes: AWS Billing and Cost Management, Budgets y Tagging (2026-11-07); Terraform AWS provider `default_tags`.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
