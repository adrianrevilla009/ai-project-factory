---
name: cloud-iam-least-privilege
description: Usar al escribir políticas IAM, roles de servicio o permisos de AWS (Terraform o consola) para aplicar mínimo privilegio y evitar comodines.
metadata:
  block: "07-appsec"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# IAM de nube con mínimo privilegio

## Cuándo aplicar y cuándo no
- Aplica a políticas, roles, perfiles de instancia, IRSA/roles de pod, políticas de recurso (S3, KMS, SQS) y límites de permisos definidos en Terraform.
- No aplica a la gobernanza de la organización (SCP; ver `scp-guardrails`) ni al acceso humano (ver `identity-center-sso`). Todo es "preparado para AWS, no verificado en real": la fábrica no despliega y LocalStack no reproduce la evaluación real de IAM.

## Reglas
- **MUST NOT** usar `"Action": "*"` ni `"Resource": "*"` en políticas de workload; listar acciones y ARN concretos.
- **MUST NOT** conceder `iam:*`, `sts:AssumeRole` abierto ni `iam:PassRole` sin restringir el rol y el servicio destino (`iam:PassedToService`).
- **MUST** usar un rol por workload y entorno, con credenciales temporales (roles, IRSA); **MUST NOT** crear usuarios IAM con claves de acceso para aplicaciones.
- **MUST** acotar con condiciones cuando aplique (`aws:SourceArn`, `aws:SourceAccount`, `aws:PrincipalOrgID`, `aws:RequestedRegion`).
- **MUST** definir confianza (trust policy) con el principal exacto; en OIDC (CI, EKS) restringir `sub` y `aud`.
- **MUST** exigir permission boundaries o SCP para roles creados por equipos.
- **SHOULD** derivar permisos reales con análisis de acceso (IAM Access Analyzer, política generada a partir de CloudTrail) y revisarlos periódicamente.
- **SHOULD** políticas de recurso que denieguen acceso público y tráfico sin TLS (`aws:SecureTransport`).
- **SHOULD** validar con herramientas estáticas antes de aplicar (Checkov, `terraform validate`, Access Analyzer `validate-policy`).

## Por qué
El radio de daño de una credencial o de una vulnerabilidad (p. ej. SSRF) es lo que permita su rol. Un comodín convierte un fallo menor en toma de cuenta. La escalada de privilegios en AWS suele ir por `iam:PassRole`, `iam:CreatePolicyVersion` o `AssumeRole` abierto.

## Ejemplos
### Mal
```hcl
resource "aws_iam_policy" "app" {
  name = "app"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{ Effect = "Allow", Action = "*", Resource = "*" }]
  })
}
```
### Bien
```hcl
data "aws_iam_policy_document" "orders_reader" {
  statement {
    sid       = "ReadOrdersQueue"
    effect    = "Allow"
    actions   = ["sqs:ReceiveMessage", "sqs:DeleteMessage", "sqs:GetQueueAttributes"]
    resources = [aws_sqs_queue.orders.arn]
  }
  statement {
    sid       = "DecryptOrdersKey"
    effect    = "Allow"
    actions   = ["kms:Decrypt"]
    resources = [aws_kms_key.orders.arn]
    condition {
      test     = "StringEquals"
      variable = "kms:ViaService"
      values   = ["sqs.eu-west-1.amazonaws.com"]   # region de ejemplo
    }
  }
}
```

## Checklist de revisión
- [ ] Sin `*` en acciones ni recursos de workloads (excepciones justificadas).
- [ ] `PassRole` y `AssumeRole` acotados; trust policy exacta.
- [ ] Rol por workload; sin claves de acceso estáticas.
- [ ] Condiciones y boundary aplicados; resultado de análisis estático revisado.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Checks Checkov custom: comodín en acción/recurso | 1 | pendiente (`policies/iac-checks/`) |
| Conftest sobre plan de Terraform (sin `*:*`) | 1 | pendiente (`policies/opa-conftest/`) |
| Revisión humana de políticas con `iam:*` | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `scp-guardrails`, `identity-center-sso`, `secrets-management`, `deserialization-xxe-ssrf-traversal`, `container-and-k8s-security`.
- Fuentes: AWS IAM User Guide (security best practices, policy evaluation logic), consultada 2026-11-07, comprobar claves de condición exactas.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
