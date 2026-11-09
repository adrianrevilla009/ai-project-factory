---
name: break-glass-and-jit-access
description: "Usar al diseñar acceso privilegiado a AWS de emergencia (break-glass) y elevación temporal just-in-time, con auditoría y alertas."
metadata:
  block: "11-aws-governance"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Break-glass y acceso JIT

Skill de diseño: la fábrica nunca despliega (ADR-0004). Madurez: definido / validado estáticamente; preparado para AWS, no verificado en real.

## Cuándo aplicar y cuándo no
- Aplica al acceso administrativo a cuentas de prod y a la recuperación cuando falla la federación.
- No aplica al break-glass de Vault/Keycloak (ver `audit-and-break-glass` del bloque 14) ni al acceso rutinario (`identity-center-sso`).

## Reglas
- **MUST** que el acceso privilegiado normal sea JIT: permission set elevado asignado por tiempo limitado con aprobación y motivo (ticket).
- **MUST** tener un mecanismo break-glass para cuando el IdP o Identity Center no estén disponibles: roles IAM en cuentas clave asumibles por un número mínimo de principales, con MFA hardware.
- **MUST** que cualquier uso de break-glass dispare alerta inmediata (EventBridge sobre `AssumeRole`/`ConsoleLogin` del rol) a un canal con respuesta humana.
- **MUST** custodiar credenciales break-glass offline con doble control (dos personas) y rotarlas tras cada uso.
- **MUST** probar el procedimiento al menos cada 6 meses y registrar el resultado.
- **SHOULD** limitar la sesión (≤ 1 h) y acotar con SCP/permission boundary lo que el rol puede hacer.
- **MUST NOT** usar el usuario root para operar; reservarlo para tareas que solo root puede hacer, con MFA y alerta.
- **MUST NOT** guardar las credenciales de emergencia en el repo ni en un gestor accesible vía el mismo IdP caído.

## Por qué
Si el IdP falla durante un incidente, sin vía de emergencia no se puede operar; si la vía existe sin alertas ni custodia, es una puerta trasera permanente.

## Ejemplos
### Mal
```text
Usuario IAM "emergency" con access key en el wiki del equipo, sin alertas.
```
### Bien
```hcl
resource "aws_cloudwatch_event_rule" "break_glass_used" {
  name = "break-glass-role-assumed"
  event_pattern = jsonencode({
    source        = ["aws.sts"]
    "detail-type" = ["AWS API Call via CloudTrail"]
    detail = {
      eventName         = ["AssumeRole"]
      requestParameters = { roleArn = [aws_iam_role.break_glass.arn] }
    }
  })
}

resource "aws_cloudwatch_event_target" "page_oncall" {
  rule = aws_cloudwatch_event_rule.break_glass_used.name
  arn  = var.oncall_sns_topic_arn
}
```

## Checklist de revisión
- [ ] Elevación JIT con aprobación, motivo y caducidad.
- [ ] Rol break-glass con MFA y alerta en cada uso.
- [ ] Custodia offline con doble control; rotación tras uso.
- [ ] Simulacro en los últimos 6 meses.
- [ ] Root sin uso operativo.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: rol break-glass sin regla EventBridge asociada | 1 | pendiente: `policies/opa-conftest/` |
| Revisión del runbook y simulacro semestral | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `identity-center-sso`, `scp-guardrails`, `org-cloudtrail-config-securityhub-guardduty`, `on-call-and-runbook-links`.
- Fuentes: AWS IAM Best Practices y guía de emergency access de AWS (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
