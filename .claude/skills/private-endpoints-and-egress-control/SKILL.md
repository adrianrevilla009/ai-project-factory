---
name: private-endpoints-and-egress-control
description: "Usar al diseñar el acceso privado a servicios AWS (VPC endpoints) y la salida a Internet (NAT, egress centralizado, allowlist de dominios) desde subredes privadas."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Endpoints privados y control de egress

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a cargas en subredes privadas que llaman a S3, ECR, STS, Secrets Manager, KMS, CloudWatch, etc., y a toda salida a Internet.
- No aplica en local: no se reproducen VPC endpoints ni políticas de endpoint; en local los servicios se simulan (p. ej. MinIO), sin garantía de equivalencia.

## Reglas
- **MUST** crear gateway endpoints para S3 (y DynamoDB si se usa): no tienen coste por hora y sacan el tráfico del NAT.
- **MUST** crear interface endpoints para los servicios que usa EKS/CI (ECR api y dkr, STS, Logs, KMS, Secrets Manager) y activar `private_dns_enabled`.
- **MUST** adjuntar una política de endpoint que limite a principals y recursos de la organización (condición `aws:PrincipalOrgID`), no `"*"`.
- **MUST** poner interface endpoints en subredes de todas las AZ y un SG que solo acepte 443 desde los SG de cómputo.
- **MUST** tratar el egress como denegado por defecto: lo que sale a Internet pasa por NAT o un punto central con allowlist de dominios (AWS Network Firewall u otro proxy con FQDN).
- **MUST NOT** dar IP pública a cargas para que "salgan"; ni abrir egress 0.0.0.0/0 en SG de datos.
- **SHOULD** compartir endpoints en una VPC de servicios solo si el ahorro compensa el coste de TGW y la complejidad de DNS (ver `dns-route53-private-and-hybrid`).
- **SHOULD** medir coste: cada interface endpoint cobra por hora y AZ y por GB (TODO-VERIFY tarifas vigentes).

## Por qué
Sin endpoints, el tráfico a servicios AWS cruza el NAT (coste por GB y salida pública). Una política de endpoint reduce la exfiltración hacia cuentas ajenas. Un egress sin allowlist convierte cualquier RCE en canal de salida de datos.

## Ejemplos
### Mal
```hcl
resource "aws_route" "all_out" {
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.a.id # todo, incluido S3, por el NAT
}
```
### Bien
```hcl
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.eu-west-1.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [for rt in aws_route_table.private : rt.id]
}

resource "aws_vpc_endpoint" "sts" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.eu-west-1.sts"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = [for s in aws_subnet.private : s.id]
  security_group_ids  = [aws_security_group.endpoints.id]
  private_dns_enabled = true
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow", Principal = "*", Action = "*", Resource = "*"
      Condition = { StringEquals = { "aws:PrincipalOrgID" = var.org_id } }
    }]
  })
}
```

## Checklist de revisión
- [ ] Gateway endpoint de S3 en todas las route tables privadas.
- [ ] Interface endpoints con DNS privado, SG a 443 y política con `aws:PrincipalOrgID`.
- [ ] Egress con ruta explícita y allowlist de dominios; sin IP pública en cargas.
- [ ] Coste de endpoints estimado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_88` (sin IP pública en EC2/launch template) | 1 | herramienta Checkov (ID comprobado en la lista local) |
| Regla custom: endpoints requeridos y política no `"*"` | 1 | pendiente: `policies/iac-checks/` |
| Revisión del allowlist de egress | 4 | revisión humana en PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `vpc-multi-az-layers`, `dns-route53-private-and-hybrid`, `cloud-iam-least-privilege`, `zero-trust`, `ssrf` (ver `deserialization-xxe-ssrf-traversal`).
- Fuentes: documentación oficial de AWS PrivateLink / VPC endpoints y de AWS Network Firewall, consulta 2026-11-07, TODO-VERIFY.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
