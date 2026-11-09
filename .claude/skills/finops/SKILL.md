---
name: finops
description: "Usar al definir presupuestos, alertas de anomalías, etiquetado, rightsizing y coste unitario de un proyecto en AWS (diseño; sin cuenta real)."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# FinOps: presupuestos, anomalías, rightsizing y coste unitario

## Cuándo aplicar y cuándo no
- Aplica a todo proyecto cuya infraestructura se describa para AWS (Terraform) y a la revisión de costes del gate de arquitectura.
- No aplica a la comparación de estrategias de DR (ver `finops-of-resilience`).
- La fábrica no tiene cuenta ni facturación real (ADR-0004): los importes son estimaciones de diseño, preparado para AWS, no verificado en real. En local no se reproducen Budgets, Cost Explorer ni Cost Anomaly Detection.

## Reglas
- **MUST** definir una política de etiquetas obligatorias (`service`, `env`, `owner`, `cost-center`, `tier`) aplicada por Terraform (`default_tags`) y activarlas como etiquetas de asignación de costes.
- **MUST** declarar presupuestos como código (AWS Budgets) por entorno/servicio con umbrales de aviso (p. ej. 50/80/100% real y 100% previsto) y destinatario.
- **MUST** declarar monitores y suscripciones de Cost Anomaly Detection; las alertas pueden ir a email o a un tema SNS. La detección no es inmediata: usa datos de Cost Explorer con hasta 24 h de retraso.
- **MUST** medir un coste unitario por negocio (coste por pedido, por tenant, por 1000 peticiones) y seguirlo como métrica junto al SLO.
- **MUST** revisar rightsizing con datos de utilización de al menos 14-30 días antes de reducir; nunca por intuición, y respetando el headroom de `capacity-and-load-modeling`.
- **SHOULD** apagar entornos efímeros fuera de horario y con TTL (`ephemeral-environments`).
- **SHOULD** revisar mensualmente los 5 mayores conceptos de coste y los recursos huérfanos (volúmenes, IP elásticas, snapshots).
- **MUST NOT** comprometer Savings Plans/instancias reservadas sin carga base estable demostrada y aprobación humana.
- **MUST NOT** recortar coste a costa de backups, observabilidad mínima o headroom del tier sin ADR.

## Por qué
El coste en cloud es una propiedad de la arquitectura, y sin etiquetas no se puede atribuir. Los presupuestos avisan por importe total; las anomalías detectan cambios de patrón (por ejemplo, un bucle que multiplica llamadas). El coste unitario evita que un aumento del gasto asociado a más negocio se lea como derroche.

## Ejemplos
### Mal
```hcl
resource "aws_instance" "worker" {
  instance_type = "m5.4xlarge"   # sin tags, tamaño por costumbre
}
```
### Bien
```hcl
provider "aws" {
  default_tags {
    tags = { service = "orders", env = "prod", owner = "orders-team", cost-center = "cc-example", tier = "1" }
  }
}

resource "aws_budgets_budget" "orders_monthly" {
  name         = "orders-prod-monthly"
  budget_type  = "COST"
  limit_amount = "4000"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"
  notification {
    comparison_operator        = "GREATER_THAN"
    threshold                  = 80
    threshold_type             = "PERCENTAGE"
    notification_type          = "FORECASTED"
    subscriber_email_addresses = ["finops@example.com"]
  }
}
```
Atributos del recurso: validar con `terraform validate`/docs del provider (los recursos y sus argumentos de primer nivel se contrastaron con la documentación del provider AWS el 2026-11-08); no se ha aplicado en AWS.

## Checklist de revisión
- [ ] Etiquetas obligatorias y de asignación de costes.
- [ ] Presupuestos y monitores de anomalías como código.
- [ ] Coste unitario definido y revisado.
- [ ] Rightsizing basado en datos y headroom.
- [ ] Revisión mensual y limpieza de huérfanos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov custom: recursos sin tags obligatorios | 1 | pendiente: `policies/iac-checks/` |
| Conftest: presencia de `aws_budgets_budget` por entorno | 1 | pendiente: `policies/opa-conftest/` |
| Revisión humana de compromisos (Savings Plans) | 4 | gate |

## Relacionados, fuentes y mantenimiento
- Relacionados: `finops-of-resilience`, `capacity-and-load-modeling`, `ephemeral-environments`, `cloud-iam-least-privilege`.
- Fuentes (verificado 2026-11-07): https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
