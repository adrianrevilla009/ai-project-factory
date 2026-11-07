---
name: hybrid-identity-and-networking
description: "Usar al conectar entornos on-prem con la nube: federación de identidad (OIDC/Keycloak), VPN o enlace dedicado, DNS y direccionamiento sin solapes."
metadata:
  block: "21-on-prem-hybrid"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "human"
---

# Identidad y red híbridas

## Cuándo aplicar y cuándo no
- Aplica cuando cargas on-prem y en la nube deben comunicarse y compartir identidad.
- Referencia T3, borrador de diseño: preparado para AWS, no verificado en real; la fábrica no despliega (ADR-0004).

## Reglas
- **MUST** un único proveedor de identidad de referencia (Keycloak) federado por OIDC; las cuentas de servicio usan identidades de carga de trabajo, no claves estáticas.
- **MUST** planificar rangos CIDR sin solapes entre sitios, nube y pods/servicios antes de conectar nada.
- **MUST** cifrado en tránsito (VPN IPsec o enlace dedicado más TLS/mTLS) y mínimo privilegio en rutas y firewalls.
- **MUST** DNS híbrido con zonas y reenvío condicional documentados.
- **SHOULD** un segundo camino de red para redundancia.
- **MUST NOT** abrir rangos completos entre sitios; permitir solo puertos y destinos necesarios (`zero-trust`).

## Por qué
Los solapes de CIDR y la identidad duplicada son imposibles de arreglar sin reconstruir; hay que decidirlos antes.

## Ejemplos
### Mal
```text
On-prem 10.0.0.0/16  <->  VPC 10.0.0.0/16   (solape)
allow any any between sites
```
### Bien
```text
On-prem 10.10.0.0/16 | Cloud 10.20.0.0/16 | Pods 10.244.0.0/16 | Services 10.96.0.0/12
allow tcp/443 from 10.10.5.0/24 to 10.20.8.0/24
```

## Checklist de revisión
- [ ] Plan CIDR sin solapes.
- [ ] Federación OIDC documentada; sin claves estáticas.
- [ ] Reglas de red mínimas y cifradas.
- [ ] DNS híbrido definido.

## Enforcement
| Mecanismo | Nivel | Dónde está |
|---|---|---|
| Revisión de diseño de red e identidad | 4 | revisión humana |
| Chequeos IaC de reglas abiertas | 1 | pendiente (`policies/iac-checks/`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `zero-trust`, `authn-oidc-oauth2`, `identity-center-sso`, `kubernetes-on-prem`.
- Fuentes: TODO-VERIFY documentación oficial de Keycloak (https://www.keycloak.org/documentation) y del proveedor de VPN.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T3
