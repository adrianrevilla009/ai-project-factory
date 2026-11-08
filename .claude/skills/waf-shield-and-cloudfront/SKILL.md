---
name: waf-shield-and-cloudfront
description: "Usar al proteger endpoints públicos en AWS: AWS WAF, Shield, CloudFront delante de ALB/S3, bloqueo de acceso directo al origen y reglas de tasa."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# WAF, Shield y CloudFront

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a todo endpoint accesible desde Internet (API pública, frontend React, descargas).
- No aplica a servicios solo internos. En local no se reproducen WAF, Shield ni CloudFront; la protección de aplicación (rate limiting, validación) debe existir igualmente en el código (ver `dos-and-rate-limiting`).

## Reglas
- **MUST** poner CloudFront delante de frontends y APIs públicas, o como mínimo un WAF regional en el ALB.
- **MUST** asociar un `aws_wafv2_web_acl`: scope `CLOUDFRONT` (se crea en us-east-1) o `REGIONAL` (misma región que el ALB).
- **MUST** incluir grupos gestionados básicos (p. ej. `AWSManagedRulesCommonRuleSet`) y una regla de tasa; desplegar reglas nuevas primero en modo `count` y pasar a `block` tras revisar logs.
- **MUST** activar logging del WAF hacia el archivo de logs (ver `flow-logs-and-network-observability`) con redacción de cabeceras sensibles.
- **MUST** impedir el acceso directo al origen: el SG del ALB solo admite la prefix list gestionada de CloudFront y se exige una cabecera secreta rotada, o se usa VPC origin si está disponible (comprobar al fijar la versión).
- **MUST** usar Origin Access Control (OAC) para orígenes S3, con el bucket privado.
- **MUST NOT** depender del WAF como única defensa: validación de entrada y authz siguen en la aplicación.
- **SHOULD** usar Shield Standard (incluido); Shield Advanced es de pago y solo se adopta con decisión explícita (D16).
- **SHOULD** forzar HTTPS al viewer, TLS 1.2 como mínimo y cabeceras de seguridad (ver `security-headers-cors-csrf`).

## Por qué
Un ALB público sin CloudFront ni WAF expone directamente la aplicación a escaneo y abuso. Si el origen es alcanzable saltándose CloudFront, el WAF se puede evitar. El modo `count` evita cortes por falsos positivos.

## Ejemplos
### Mal
```hcl
resource "aws_security_group_rule" "alb_in" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"] # el origen se puede atacar sin pasar por el WAF
  security_group_id = aws_security_group.alb.id
}
```
### Bien
```hcl
data "aws_ec2_managed_prefix_list" "cloudfront" {
  name = "com.amazonaws.global.cloudfront.origin-facing"
}

resource "aws_vpc_security_group_ingress_rule" "alb_from_cloudfront" {
  security_group_id = aws_security_group.alb.id
  prefix_list_id    = data.aws_ec2_managed_prefix_list.cloudfront.id
  from_port         = 443
  to_port           = 443
  ip_protocol       = "tcp"
  description       = "HTTPS from CloudFront only"
}

resource "aws_wafv2_web_acl" "edge" {
  provider = aws.us_east_1 # scope CLOUDFRONT exige us-east-1
  name     = "edge"
  scope    = "CLOUDFRONT"
  default_action {
    allow {}
  }
  rule {
    name     = "rate"
    priority = 1
    action {
      block {}
    }
    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "rate"
      sampled_requests_enabled   = true
    }
  }
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "edge"
    sampled_requests_enabled   = true
  }
}
```

## Checklist de revisión
- [ ] CloudFront o WAF regional delante de todo endpoint público.
- [ ] Origen cerrado a CloudFront (prefix list + cabecera/VPC origin).
- [ ] Reglas gestionadas + tasa; reglas nuevas en `count` primero.
- [ ] Logging del WAF activo; OAC en S3.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_68` (WAF en CloudFront), `CKV2_AWS_28` (ALB público con WAF), `CKV_AWS_176` (logging WAF), `CKV_AWS_174` (TLS 1.2 viewer) | 1 | herramienta Checkov (IDs comprobados en la lista local) |
| Decisión de adoptar Shield Advanced | 4 | revisión humana (coste, D16) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `alb-nlb-and-tls-termination`, `dos-and-rate-limiting`, `security-headers-cors-csrf`, `owasp-top10-and-api-top10`.
- Fuentes: documentación oficial de AWS WAF, AWS Shield y CloudFront (origin access control, prefix list gestionada) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
