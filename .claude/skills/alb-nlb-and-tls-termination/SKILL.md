---
name: alb-nlb-and-tls-termination
description: "Usar al elegir y configurar balanceadores AWS (ALB vs NLB), listeners, certificados ACM y dónde terminar TLS (borde, balanceador o malla)."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# ALB, NLB y terminación TLS

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a cualquier balanceador de entrada (público o interno) en eu-west-1/eu-central-1.
- No aplica al tráfico este-oeste dentro de la malla (ver mTLS en el bloque Istio). En local no se reproduce ALB/NLB/ACM: se usa un Gateway de Istio o ingress de kind, sin equivalencia de comportamiento.

## Reglas
- **MUST** elegir ALB para HTTP/HTTPS/gRPC (rutas, host, WAF) y NLB para TCP/TLS, IP estática o PrivateLink.
- **MUST** servir solo HTTPS en listeners públicos; el puerto 80 solo redirige a 443 (HTTP 301).
- **MUST** usar certificados de ACM (renovación automática) por región; para CloudFront el certificado vive en us-east-1.
- **MUST** fijar una política TLS moderna (TLS 1.2 mínimo, preferible 1.3) con una `ssl_policy` explícita, no la heredada por defecto (comprobar nombre vigente).
- **MUST** activar `drop_invalid_header_fields`, access logs a S3 y `enable_deletion_protection` en producción.
- **MUST NOT** terminar TLS en el balanceador y reenviar HTTP en claro hacia pods con datos sensibles: recifrar hacia el backend (HTTPS al target o mTLS de malla).
- **SHOULD** usar `target-type: ip` con AWS Load Balancer Controller en EKS (ver `eks-networking`) y health checks dedicados.
- **SHOULD** un balanceador interno por frontera de confianza; SG del balanceador como único origen permitido en los SG de cómputo.

## Por qué
La terminación de TLS decide quién ve el tráfico en claro. Dejar el segmento balanceador-pod sin cifrar rompe el modelo zero-trust. Las políticas TLS por defecto cambian con el tiempo; fijarlas hace la configuración revisable.

## Ejemplos
### Mal
```hcl
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.public.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward" # tráfico en claro hacia el backend
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```
### Bien
```hcl
resource "aws_lb" "public" {
  name                       = "orders-public"
  load_balancer_type         = "application"
  subnets                    = [for s in aws_subnet.public : s.id]
  security_groups            = [aws_security_group.alb.id]
  drop_invalid_header_fields = true
  enable_deletion_protection = true
  access_logs {
    bucket  = var.alb_logs_bucket
    enabled = true
  }
}

resource "aws_lb_listener" "http_redirect" {
  load_balancer_arn = aws_lb.public.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.public.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06" # comprobar vigente
  certificate_arn   = aws_acm_certificate_validation.api.certificate_arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
```

## Checklist de revisión
- [ ] ALB vs NLB justificado; listener 80 solo redirige.
- [ ] Certificado ACM de la región correcta y política TLS explícita.
- [ ] Access logs, deletion protection y cabeceras inválidas descartadas.
- [ ] Segmento hacia el backend cifrado o justificado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_2`, `CKV_AWS_103`, `CKV2_AWS_20`, `CKV_AWS_91`, `CKV_AWS_131`, `CKV_AWS_150` | 1 | herramienta Checkov (IDs comprobados en la lista local) |
| Revisión de la decisión de terminación TLS | 4 | revisión humana en PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `waf-shield-and-cloudfront`, `eks-networking`, `crypto-tls-mtls-key-rotation`, `ingress-and-egress-gateways`.
- Fuentes: documentación oficial de Elastic Load Balancing (listeners, políticas de seguridad) y ACM (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
