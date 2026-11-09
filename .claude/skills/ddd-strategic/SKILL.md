---
name: ddd-strategic
description: "Usar al delimitar dominios, bounded contexts y relaciones entre equipos o servicios, antes de decidir módulos o microservicios."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# DDD estratégico

## Cuándo aplicar y cuándo no
- Aplica al partir un sistema en módulos/servicios, al integrar con sistemas ajenos y al asignar equipos a áreas de negocio.
- No aplica a un CRUD sin lógica de dominio ni a scripts puntuales; ahí el coste del modelado supera el beneficio.

## Reglas
- **MUST** identificar subdominios (core, supporting, generic) y concentrar el esfuerzo de diseño en el core.
- **MUST** definir cada bounded context con nombre, responsabilidad, lenguaje ubicuo propio y dueño (equipo).
- **MUST** documentar el context map: para cada relación indicar el patrón (Customer/Supplier, Conformist, Anti-Corruption Layer, Shared Kernel, Open Host Service/Published Language).
- **MUST NOT** compartir el modelo de dominio ni el esquema de BD entre contexts; se integran por contratos (API o eventos).
- **MUST NOT** usar un único modelo "canónico" de empresa para todos los contexts.
- **SHOULD** alinear un bounded context con un módulo (monolito modular) o un servicio, nunca varios contexts en un mismo módulo.
- **SHOULD** comprar/adoptar solución estándar para subdominios genéricos (identidad con Keycloak, D-decisiones del repo) en lugar de modelarlos.
- **SHOULD** usar Event Storming para descubrir contexts; el resultado se guarda como ADR o documento de arquitectura.

## Por qué
Los límites mal puestos son la causa principal de microservicios acoplados y monolitos enredados. La misma palabra ("Cliente") significa cosas distintas en Ventas y en Facturación; forzar un único modelo produce clases gigantes y cambios que afectan a todos. Los límites se eligen por lenguaje y cambio de negocio, no por capas técnicas.

## Ejemplos
### Mal
```text
Servicio "customer-service" con la entidad Customer usada por Ventas, Facturación y Soporte;
los tres equipos modifican la misma tabla `customer` (40 columnas).
```
### Bien
```text
Context Sales:    Customer = {id, segment, creditScore}
Context Billing:  Payer    = {id, taxId, billingAddress}
Context Support:  Requester = {id, contactChannel}
Relación Sales -> Billing: Customer/Supplier, evento CustomerRegistered (Published Language).
Relación Billing -> ERP legado: Anti-Corruption Layer.
```
Fragmento de context map (documento `docs/architecture/context-map.md` del proyecto generado):
```text
| Upstream | Downstream | Patrón               | Contrato                 |
|----------|------------|----------------------|--------------------------|
| Sales    | Billing    | Customer/Supplier    | CustomerRegistered v1    |
| ERP      | Billing    | Anti-Corruption Layer| adaptador `ErpGateway`   |
```

## Checklist de revisión
- [ ] Cada subdominio está clasificado (core/supporting/generic).
- [ ] Cada context tiene dueño, responsabilidad y glosario propio.
- [ ] Existe context map con patrón por relación.
- [ ] Ningún context lee la BD de otro.
- [ ] No hay modelo canónico global.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del context map en el gate de arquitectura | 4 | `gates/` (fase de arquitectura) |
| Agente revisor de arquitectura | 3 | pendiente (agente `architecture-reviewer`) |
| Aislamiento entre contexts con ArchUnit | 1 | pendiente: `policies/archunit/` (ver `modular-monolith`) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `ddd-tactical`, `anti-corruption-layer`, `modular-monolith`, `microservices-decision-guide`, `connascence-and-coupling`.
- Fuentes: Evans, "Domain-Driven Design" (2003); Vernon, "Implementing Domain-Driven Design" (2013).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
