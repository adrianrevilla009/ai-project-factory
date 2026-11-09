---
name: cidr-planning-and-ipam
description: "Usar al diseñar rangos CIDR de VPC, subredes o EKS, o al introducir VPCs nuevas que deban conectarse por TGW, peering o VPN sin solapamientos."
metadata:
  block: "12-aws-networking"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Planificación de CIDR e IPAM

Madurez: definido / validado estáticamente. Preparado para AWS, no verificado en real. La fábrica nunca despliega (ADR-0004).

## Cuándo aplicar y cuándo no
- Aplica a toda VPC, subred o rango secundario (pods de EKS) y a cualquier conexión futura entre redes (TGW, peering, VPN, Direct Connect).
- No aplica a redes locales de desarrollo (kind/docker): no se reproduce en local el direccionamiento de AWS; allí solo importa no chocar con la red corporativa del desarrollador.

## Reglas
- **MUST** asignar los CIDR desde un plan central único (fichero versionado o AWS IPAM), nunca a mano por equipo.
- **MUST NOT** solapar CIDR entre VPCs, regiones, cuentas ni con on-premises: un solapamiento no se arregla después sin recrear la VPC.
- **MUST** reservar bloques por región (eu-west-1 primaria, eu-central-1 secundaria, D6) y por entorno, dejando hueco de crecimiento (>= 50 % libre).
- **MUST** dimensionar VPC en /16 (workloads) y subredes /20 (privadas) o /24 (públicas, datos pequeños); AWS reserva 5 direcciones por subred.
- **SHOULD** usar `aws_vpc_ipam` con pools por región y `ipv4_ipam_pool_id` en `aws_vpc`, de modo que el solapamiento sea imposible por construcción.
- **SHOULD** dar a EKS un CIDR secundario dedicado a pods (p. ej. rango 100.64.0.0/10, ver `eks-networking`) para no agotar IPs.
- **MUST NOT** usar la VPC por defecto ni rangos 172.31.0.0/16 de la VPC por defecto.
- **MUST** documentar el plan en una tabla (región, entorno, CIDR, propietario, estado).

## Por qué
Los CIDR son la decisión de red más difícil de revertir: TGW, peering y VPN exigen rangos disjuntos. Un plan central barato hoy evita migrar VPCs mañana. IPAM convierte la regla en una restricción técnica.

## Ejemplos
### Mal
```hcl
resource "aws_vpc" "orders" {
  cidr_block = "10.0.0.0/16" # copiado de otro equipo, nadie sabe si choca
}
```
### Bien
```hcl
resource "aws_vpc_ipam" "main" {
  operating_regions { region_name = "eu-west-1" }
  operating_regions { region_name = "eu-central-1" }
}

resource "aws_vpc_ipam_pool" "euw1_prod" {
  address_family = "ipv4"
  ipam_scope_id  = aws_vpc_ipam.main.private_default_scope_id
  locale         = "eu-west-1"
}

resource "aws_vpc_ipam_pool_cidr" "euw1_prod" {
  ipam_pool_id = aws_vpc_ipam_pool.euw1_prod.id
  cidr         = "10.16.0.0/12" # plan: eu-west-1 prod
}

resource "aws_vpc" "orders" {
  ipv4_ipam_pool_id   = aws_vpc_ipam_pool.euw1_prod.id
  ipv4_netmask_length = 16
  depends_on          = [aws_vpc_ipam_pool_cidr.euw1_prod]
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Planifica los rangos de toda la organización desde el principio con un gestor central: sin solapamientos entre cuentas, regiones ni redes locales.
- Reserva espacio para crecer y para redes que aún no existen.
### Trampas frecuentes
- Rangos solapados que impiden conectar redes después.
- Redes demasiado pequeñas que se agotan.
- Asignación a mano en hojas de cálculo.
- No reservar rangos para pods o servicios en clústeres.
- Usar el mismo rango en todos los entornos.
### Evidencia
- Un inventario central de rangos validado automáticamente contra solapamientos.

## Checklist de revisión
- [ ] El CIDR viene del plan/IPAM y está en la tabla de asignaciones.
- [ ] No solapa con otras VPC, regiones ni on-premises.
- [ ] Hay hueco de crecimiento y rango para pods de EKS.
- [ ] No se usa la VPC por defecto.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Checkov `CKV_AWS_148` (no VPC por defecto) | 1 | herramienta Checkov, comprobado en la lista local de checks |
| Regla Conftest de CIDR disjuntos contra el plan | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de la tabla de asignaciones | 4 | revisión humana en PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `vpc-multi-az-layers`, `transit-gateway-hub-and-spoke`, `eks-networking`, `regions-and-data-residency`.
- Fuentes: documentación oficial de Amazon VPC IPAM y de dimensionado de VPC/subredes (consulta 2026-11-07).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
