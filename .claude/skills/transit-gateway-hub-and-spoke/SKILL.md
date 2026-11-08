---
name: transit-gateway-hub-and-spoke
description: "Usar al conectar varias VPC o cuentas con Transit Gateway: tablas de rutas segmentadas, inspección centralizada y peering entre eu-west-1 y eu-central-1."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Transit Gateway hub-and-spoke

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica cuando hay 3 o más VPC/cuentas que deben comunicarse, o salida/inspección centralizada, o conexión con on-premises.
- No aplica a 2 VPC con un único flujo (basta peering) ni al entorno local: no se reproduce TGW en local.

## Reglas
- **MUST** crear un TGW por región (eu-west-1 y eu-central-1, D6) en la cuenta de red y compartirlo con RAM; los spokes solo crean attachments.
- **MUST** desactivar asociación y propagación por defecto (`default_route_table_association/propagation = "disable"`) y gestionar tablas explícitas (spokes, shared, inspección).
- **MUST** segmentar: las VPC de entornos distintos (dev/prod) no deben tener ruta entre sí; la ausencia de ruta es el control.
- **MUST** activar `appliance_mode_support = "enable"` en el attachment de la VPC de inspección para mantener simetría por AZ.
- **MUST** usar rutas estáticas en el peering inter-región (no hay propagación dinámica) y registrarlas en código.
- **MUST NOT** usar rutas 0.0.0.0/0 en spokes hacia el TGW sin pasar por inspección/egress controlado (ver `private-endpoints-and-egress-control`).
- **SHOULD** usar un attachment por AZ con subredes /28 dedicadas de TGW.
- **SHOULD** evitar TGW si el tráfico entre VPC es masivo y el coste por GB lo desaconseja (ver `cross-region-connectivity-and-cost`).

## Por qué
Sin tablas explícitas, el TGW por defecto produce una malla plana donde dev alcanza prod. Segmentar por tabla de rutas hace el aislamiento auditable en código. El appliance mode evita que el tráfico de retorno cambie de AZ y rompa el firewall con estado.

## Ejemplos
### Mal
```hcl
resource "aws_ec2_transit_gateway" "main" {
  # asociación y propagación por defecto: todo habla con todo
}
```
### Bien
```hcl
resource "aws_ec2_transit_gateway" "euw1" {
  description                     = "hub eu-west-1"
  default_route_table_association = "disable"
  default_route_table_propagation = "disable"
  auto_accept_shared_attachments  = "disable"
}

resource "aws_ec2_transit_gateway_route_table" "prod" {
  transit_gateway_id = aws_ec2_transit_gateway.euw1.id
}

resource "aws_ec2_transit_gateway_vpc_attachment" "orders_prod" {
  transit_gateway_id = aws_ec2_transit_gateway.euw1.id
  vpc_id             = aws_vpc.orders.id
  subnet_ids         = [for s in aws_subnet.tgw : s.id]
}

resource "aws_ec2_transit_gateway_route_table_association" "orders_prod" {
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_vpc_attachment.orders_prod.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.prod.id
}

resource "aws_ec2_transit_gateway_route" "to_euc1" {
  destination_cidr_block         = "10.32.0.0/12" # plan eu-central-1
  transit_gateway_attachment_id  = aws_ec2_transit_gateway_peering_attachment.euw1_euc1.id
  transit_gateway_route_table_id = aws_ec2_transit_gateway_route_table.prod.id
}
```

## Checklist de revisión
- [ ] Asociación/propagación por defecto desactivadas; tablas por segmento.
- [ ] dev y prod sin ruta entre sí.
- [ ] Appliance mode en la VPC de inspección.
- [ ] Rutas estáticas del peering en código; CIDR disjuntos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_331` (TGW sin auto-accept de attachments, ID comprobado en la lista local) | 1 | herramienta Checkov |
| Regla custom: asociación/propagación por defecto desactivadas | 1 | pendiente: `policies/iac-checks/` |
| Revisión de la matriz de rutas entre segmentos | 4 | revisión humana en PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cidr-planning-and-ipam`, `cross-region-connectivity-and-cost`, `flow-logs-and-network-observability`, `zero-trust`.
- Fuentes: documentación oficial de AWS Transit Gateway (tablas de rutas, peering, appliance mode) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
