---
name: identity-center-sso
description: "Usar al diseñar el acceso humano a cuentas AWS con IAM Identity Center: grupos, permission sets, federación con Keycloak y sesiones cortas."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# IAM Identity Center (SSO)

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica al acceso de personas (consola y CLI) a las cuentas de la organización.
- No aplica a identidades de carga (IRSA / Pod Identity, bloque de Kubernetes) ni a usuarios finales de la aplicación (Keycloak, D-identidad).

## Reglas
- **MUST** dar acceso humano solo vía Identity Center con credenciales temporales; cero usuarios IAM con claves de larga duración.
- **MUST** asignar permission sets a grupos, nunca a usuarios individuales.
- **MUST** federar el IdP corporativo (Keycloak como IdP externo vía SAML/SCIM) y exigir MFA en el IdP.
- **MUST** limitar la duración de sesión (por defecto ≤ 8 h; admin ≤ 1 h).
- **MUST** separar permission sets: `ReadOnly`, `Developer`, `Deployer` (CI), `PlatformAdmin`, `SecurityAudit`.
- **SHOULD** gestionar grupos y asignaciones por Terraform.
- **SHOULD** ubicar la instancia en eu-west-1 (región primaria, D6); la región de la instancia es difícil de cambiar.
- **MUST NOT** conceder `AdministratorAccess` permanente a nadie en prod; ver `break-glass-and-jit-access`.

## Por qué
Las claves de larga duración se filtran y no caducan. Grupos + permission sets hacen auditable quién puede qué y permiten el offboarding en un solo punto (el IdP).

## Ejemplos
### Mal
```hcl
resource "aws_iam_user" "ana" { name = "ana" }
resource "aws_iam_user_policy_attachment" "ana_admin" {
  user       = aws_iam_user.ana.name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
```
### Bien
```hcl
resource "aws_ssoadmin_permission_set" "developer" {
  name             = "Developer"
  instance_arn     = local.sso_instance_arn
  session_duration = "PT4H"
}

resource "aws_ssoadmin_account_assignment" "dev_team_orders_dev" {
  instance_arn       = local.sso_instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.developer.arn
  principal_id       = var.group_orders_developers_id
  principal_type     = "GROUP"
  target_id          = var.account_orders_dev_id
  target_type        = "AWS_ACCOUNT"
}
```

## Checklist de revisión
- [ ] Sin `aws_iam_user` ni access keys para personas.
- [ ] Asignaciones a grupos, no a usuarios.
- [ ] MFA exigido en el IdP.
- [ ] `session_duration` acotada.
- [ ] Sin admin permanente en prod.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Checkov custom: `aws_iam_user`, `aws_iam_access_key`, `principal_type = "USER"` | 1 | pendiente: `policies/iac-checks/` |
| Hook de secretos bloquea claves AWS en repo | 2 | `.claude/hooks/` (ver bloque de seguridad) |
| Revisión de permission sets | 3 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `break-glass-and-jit-access`, `scp-guardrails`, `control-tower-and-account-factory`.
- Fuentes: IAM Identity Center User Guide (2026-11-07).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
