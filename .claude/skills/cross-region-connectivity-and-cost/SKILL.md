---
name: cross-region-connectivity-and-cost
description: "Usar al conectar eu-west-1 con eu-central-1 o estimar costes de red: peering TGW, transferencia entre AZ/regiones, NAT, endpoints y replicación."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Conectividad entre regiones y coste de red

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a tráfico entre eu-west-1 (primaria) y eu-central-1 (secundaria, D6), entre AZ y hacia Internet, y a cualquier estimación de coste de red.
- No aplica al desarrollo local, que no genera ni refleja costes de transferencia de AWS.

## Reglas
- **MUST** conectar regiones con peering de TGW (rutas estáticas, ver `transit-gateway-hub-and-spoke`) o VPC peering inter-región para casos simples; el tráfico viaja por la red de AWS, no por Internet.
- **MUST** mantener las llamadas síncronas dentro de una región; entre regiones solo replicación asíncrona y tráfico de control (ver `consistency-and-cap-tradeoffs`, `cell-based-architecture`).
- **MUST** respetar la residencia de datos: ningún dato personal se replica a una región no autorizada (ver `regions-and-data-residency`; normativa = borrador por confirmar con fuente oficial).
- **MUST** estimar el coste antes de añadir un flujo: transferencia entre regiones, entre AZ, procesamiento de NAT/TGW/endpoints y salida a Internet se cobran por GB (TODO-VERIFY tarifas vigentes; no copiar cifras de memoria).
- **MUST NOT** construir arquitecturas con tráfico entre AZ innecesario: usar enrutado consciente de topología (topology aware routing) y NAT por AZ.
- **SHOULD** comprimir y agrupar la replicación; preferir réplicas de lectura locales a lecturas remotas.
- **SHOULD** reducir salida por NAT con endpoints de gateway/interfaz (ver `private-endpoints-and-egress-control`) y CloudFront para servir caché.
- **SHOULD** etiquetar y presupuestar el coste de red por producto (ver `tagging-cost-allocation-budgets`).
- **SHOULD** revisar mensualmente los mayores emisores de transferencia con flow logs.

## Por qué
El coste de red es el gasto que más sorprende: no aparece en el diseño de la aplicación y crece con el tráfico. Una llamada síncrona entre regiones añade además latencia y acopla la disponibilidad de ambas. Estimar antes de construir es barato; corregir después, no.

## Ejemplos
### Mal
```yaml
# El servicio de pedidos en eu-west-1 consulta de forma síncrona el catálogo de eu-central-1
catalog:
  base-url: https://catalog.euc1.internal.example.com
  # cada petición cruza la región y se cobra por GB
```
### Bien
```yaml
# Catálogo replicado de forma asíncrona; lectura local, sin dependencia síncrona entre regiones
catalog:
  base-url: https://catalog.euw1.internal.example.com
  replication:
    source-region: eu-west-1
    target-region: eu-central-1
    mode: async
```
```hcl
resource "aws_ec2_transit_gateway_peering_attachment" "euw1_euc1" {
  transit_gateway_id      = aws_ec2_transit_gateway.euw1.id
  peer_transit_gateway_id = var.euc1_tgw_id
  peer_region             = "eu-central-1"
}
```

## Checklist de revisión
- [ ] Sin llamadas síncronas entre regiones; replicación asíncrona.
- [ ] Estimación de coste de cada flujo nuevo (regiones, AZ, NAT/TGW/endpoints).
- [ ] Residencia de datos comprobada para lo replicado.
- [ ] Presupuesto y etiquetas de red; revisión mensual de grandes emisores.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Estimación de coste en el PR | 4 | revisión humana |
| Regla custom: alerta ante peering o rutas inter-región no inventariadas | 1 | pendiente: `policies/iac-checks/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `transit-gateway-hub-and-spoke`, `private-endpoints-and-egress-control`, `global-accelerator-and-failover-routing`, `regions-and-data-residency`, `tagging-cost-allocation-budgets`.
- Fuentes: páginas oficiales de precios de AWS (transferencia de datos, NAT Gateway, Transit Gateway) y documentación de peering de TGW, consulta 2026-11-07, TODO-VERIFY (sin cifras en este skill).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
