---
name: global-accelerator-and-failover-routing
description: "Usar al diseñar la entrada multirregión eu-west-1/eu-central-1: elegir entre Route 53 (failover, latencia) y Global Accelerator, health checks y reparto de tráfico."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Global Accelerator y enrutado de failover

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica al diseño de la entrada activa-pasiva o activa-activa entre eu-west-1 (primaria) y eu-central-1 (secundaria, D6).
- No aplica a servicios de una sola región. En local no se reproduce el failover regional; solo se puede simular por scripts, sin equivalencia.

## Reglas
- **MUST** decidir y documentar el modo: activa-pasiva (RTO mayor, más simple) o activa-activa (requiere datos replicables, sin doble escritura Postgres+NoSQL).
- **MUST** elegir la herramienta: Route 53 (failover o latencia con health checks) cuando basta DNS; Global Accelerator (IP anycast estáticas, conmutación sin esperar caché DNS) cuando el RTO o las IP fijas lo exigen.
- **MUST** respaldar el failover con health checks que prueben la dependencia crítica (endpoint `/health/ready`), no solo que el balanceador responda.
- **MUST** definir un TTL bajo (<= 60 s) en registros de failover de Route 53 y asumir que algunos resolvers lo ignoran.
- **MUST** ensayar el failover (game day) y el failback; un camino de failover no probado no cuenta.
- **MUST NOT** conmutar tráfico a una región cuyos datos no estén replicados o cuya capacidad no esté dimensionada; documentar RPO/RTO.
- **SHOULD** usar `traffic_dial_percentage` de los endpoint groups de Global Accelerator para drenar o hacer canary regional.
- **SHOULD** activar flow logs del acelerador hacia el archivo de logs.
- **SHOULD** valorar el coste fijo y por GB de Global Accelerator frente a Route 53 (TODO-VERIFY tarifas).

## Por qué
DNS-failover depende de cachés fuera de nuestro control; un acelerador conmuta en la red de AWS pero añade coste y un servicio más. Un health check superficial mantiene tráfico en una región rota. El valor del diseño está en el ensayo y en los datos replicados, no en el recurso Terraform.

## Ejemplos
### Mal
```hcl
resource "aws_route53_record" "api" {
  zone_id = var.zone_id
  name    = "api.example.com"
  type    = "A"
  ttl     = 3600 # el failover tardará una hora en notarse
  records = ["192.0.2.10"]
}
```
### Bien
```hcl
resource "aws_route53_health_check" "euw1" {
  fqdn              = "api-euw1.example.com"
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health/ready"
  failure_threshold = 3
  request_interval  = 10
}

resource "aws_route53_record" "api_primary" {
  zone_id         = var.zone_id
  name            = "api.example.com"
  type            = "CNAME"
  ttl             = 60
  set_identifier  = "euw1"
  records         = ["api-euw1.example.com"]
  health_check_id = aws_route53_health_check.euw1.id
  failover_routing_policy { type = "PRIMARY" }
}

resource "aws_route53_record" "api_secondary" {
  zone_id        = var.zone_id
  name           = "api.example.com"
  type           = "CNAME"
  ttl            = 60
  set_identifier = "euc1"
  records        = ["api-euc1.example.com"]
  failover_routing_policy { type = "SECONDARY" }
}
```

## Checklist de revisión
- [ ] Modo (activa-pasiva/activa-activa) y RPO/RTO documentados.
- [ ] Route 53 vs Global Accelerator justificado, con coste.
- [ ] Health check profundo y TTL bajo.
- [ ] Failover y failback ensayados; capacidad y datos en la región secundaria.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_75` (flow logs de Global Accelerator, ID comprobado en la lista local) | 1 | herramienta Checkov |
| Evidencia del game day de failover | 4 | revisión humana (acta en el repo del proyecto) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `dns-route53-private-and-hybrid`, `alb-nlb-and-tls-termination`, `cross-region-connectivity-and-cost`, `regions-and-data-residency`, `multi-cluster-and-dr`.
- Fuentes: documentación oficial de Route 53 (failover, health checks) y AWS Global Accelerator (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
