---
name: dns-route53-private-and-hybrid
description: "Usar al diseñar DNS en AWS: zonas privadas de Route 53, Resolver inbound/outbound para híbrido, asociación entre VPC/cuentas y registros de failover."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# DNS: Route 53 privado e híbrido

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a nombres internos entre VPC/cuentas, resolución con on-premises y registros públicos de la plataforma.
- No aplica a la resolución dentro del clúster (CoreDNS) ni a `external-dns` de Kubernetes salvo su zona destino. En local no se reproduce Route 53; se usa DNS del clúster o /etc/hosts.

## Reglas
- **MUST** usar un esquema de nombres por entorno y región (p. ej. `orders.prod.euw1.internal.example.com`) y no reutilizar el mismo nombre privado con IP distinta entre regiones.
- **MUST** crear zonas privadas en la cuenta de red y asociarlas a las VPC consumidoras (`aws_route53_vpc_association_authorization` + `aws_route53_zone_association` entre cuentas).
- **MUST** tener `enable_dns_support` y `enable_dns_hostnames` activos en las VPC con zonas privadas o endpoints.
- **MUST** desplegar Resolver endpoints con al menos 2 IP en AZ distintas: inbound (on-prem hacia AWS) y outbound (AWS hacia on-prem con reglas por dominio).
- **MUST NOT** hacer forwarding recursivo de todo (`.`) a on-premises; solo dominios corporativos concretos.
- **SHOULD** activar DNSSEC en zonas públicas y query logging de Resolver/zonas hacia el archivo de logs (ver `flow-logs-and-network-observability`).
- **SHOULD** usar TTL bajos (<= 60 s) solo en registros de failover; el resto con TTL moderado.
- **SHOULD** gestionar los registros de los balanceadores como alias, no CNAME, en el ápice.

## Por qué
El DNS es dependencia de todo: un forward mal acotado rompe la resolución de servicios AWS, y una zona privada sin asociar produce fallos intermitentes por VPC. Centralizar zonas y reglas en la cuenta de red mantiene un único punto de cambio auditable.

## Ejemplos
### Mal
```hcl
resource "aws_route53_resolver_rule" "all" {
  domain_name          = "." # todo el DNS al servidor on-prem
  rule_type            = "FORWARD"
  resolver_endpoint_id = aws_route53_resolver_endpoint.out.id
  target_ip { ip = "192.0.2.10" }
}
```
### Bien
```hcl
resource "aws_route53_zone" "internal" {
  name = "internal.example.com"
  vpc { vpc_id = aws_vpc.hub.id }
}

resource "aws_route53_resolver_endpoint" "out" {
  name               = "onprem-out"
  direction          = "OUTBOUND"
  security_group_ids = [aws_security_group.dns.id]
  dynamic "ip_address" {
    for_each = aws_subnet.private # 2+ AZ
    content { subnet_id = ip_address.value.id }
  }
}

resource "aws_route53_resolver_rule" "corp" {
  domain_name          = "corp.example.com"
  rule_type            = "FORWARD"
  resolver_endpoint_id = aws_route53_resolver_endpoint.out.id
  target_ip { ip = "192.0.2.10" }
}
```

## Checklist de revisión
- [ ] Zonas privadas asociadas a todas las VPC consumidoras.
- [ ] Resolver endpoints con 2+ IP en AZ distintas y SG limitado a 53.
- [ ] Reglas de forwarding por dominio, no `.`.
- [ ] DNSSEC/query logging según el tipo de zona.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV2_AWS_38` (DNSSEC en zonas públicas) y `CKV2_AWS_39` (query logging) | 1 | herramienta Checkov (IDs comprobados en la lista local) |
| Regla custom: no `domain_name = "."` en reglas FORWARD | 1 | pendiente: `policies/iac-checks/` |
| Revisión del esquema de nombres | 4 | revisión humana en PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `private-endpoints-and-egress-control`, `global-accelerator-and-failover-routing`, `transit-gateway-hub-and-spoke`.
- Fuentes: documentación oficial de Route 53 (zonas privadas) y Route 53 Resolver.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
