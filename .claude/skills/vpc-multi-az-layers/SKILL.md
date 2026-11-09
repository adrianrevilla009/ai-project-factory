---
name: vpc-multi-az-layers
description: "Usar al diseñar la topología de una VPC: capas de subredes (pública, privada, datos), reparto en AZ, NAT, tablas de rutas y security groups."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# VPC multi-AZ por capas

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a cualquier VPC nueva o revisada en eu-west-1 (primaria) o eu-central-1 (secundaria, D6).
- No aplica a redes locales: kind/docker no reproduce AZ, NAT Gateway, route tables ni security groups de AWS.

## Reglas
- **MUST** usar como mínimo 3 AZ por VPC (o 2 si la región lo limita) y la misma estructura de capas en cada una.
- **MUST** separar tres capas de subredes: pública (solo balanceadores y NAT), privada (cómputo/EKS) y datos (bases, caches), cada una con su route table.
- **MUST NOT** asignar IP pública por defecto a subredes (`map_public_ip_on_launch = false`) ni colocar cómputo o datos en subredes públicas.
- **MUST** poner un NAT Gateway por AZ y rutear cada subred privada al NAT de su propia AZ (evita tráfico y fallo cross-AZ).
- **MUST** restringir el security group por defecto (`aws_default_security_group` sin reglas) y usar SG por rol, referenciando otros SG como origen en vez de CIDR.
- **MUST NOT** abrir 0.0.0.0/0 en ingress salvo 443 hacia el balanceador público; sin SSH/RDP abierto (usar SSM Session Manager).
- **SHOULD** usar NACL solo como red de seguridad gruesa (denegar rangos conocidos); la lógica fina va en SG.
- **SHOULD** activar `enable_dns_support` y `enable_dns_hostnames` (requisito de endpoints y zonas privadas).
- **SHOULD** etiquetar subredes con rol y entorno (ver `tagging-cost-allocation-budgets`).

## Por qué
Capas con tablas de rutas distintas hacen que la exposición sea una propiedad de la topología y no de la disciplina. Un NAT por AZ elimina un punto único de fallo y el coste de transferencia entre AZ. Referenciar SG por SG evita rangos que caducan.

## Ejemplos
### Mal
```hcl
resource "aws_subnet" "app" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.16.1.0/24"
  map_public_ip_on_launch = true # cómputo con IP pública
}
resource "aws_security_group_rule" "db" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.db.id
}
```
### Bien
```hcl
resource "aws_subnet" "private" {
  for_each                = local.azs # { a = "eu-west-1a", ... }
  vpc_id                  = aws_vpc.main.id
  availability_zone       = each.value
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 4, local.private_index[each.key])
  map_public_ip_on_launch = false
}
resource "aws_route" "private_nat" {
  for_each               = aws_route_table.private # una por AZ
  route_table_id         = each.value.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.az[each.key].id
}
resource "aws_vpc_security_group_ingress_rule" "db_from_app" {
  security_group_id            = aws_security_group.db.id
  referenced_security_group_id = aws_security_group.app.id
  from_port                    = 5432
  to_port                      = 5432
  ip_protocol                  = "tcp"
  description                  = "PostgreSQL from app tier"
}
```

## Checklist de revisión
- [ ] Tres capas y tres AZ; una route table por capa/AZ.
- [ ] NAT por AZ; ninguna subred de cómputo/datos pública.
- [ ] Default SG sin reglas; SG por rol referenciando SG.
- [ ] Sin SSH/RDP ni bases abiertas a Internet.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_130` (subred sin IP pública), `CKV2_AWS_12` (default SG), `CKV_AWS_24`/`CKV_AWS_25` (SSH/RDP) | 1 | herramienta Checkov (IDs comprobados en la lista local) |
| Regla custom: un NAT por AZ | 1 | pendiente: `policies/iac-checks/` |
| Revisión de topología | 3 | agente revisor / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cidr-planning-and-ipam`, `private-endpoints-and-egress-control`, `zero-trust`, `cloud-iam-least-privilege`.
- Fuentes: documentación oficial de Amazon VPC y buenas prácticas de seguridad de VPC.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
