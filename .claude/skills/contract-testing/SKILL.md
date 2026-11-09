---
name: contract-testing
description: "Usar al decidir cómo verificar contratos entre servicios o eventos (consumer-driven, OpenAPI, AsyncAPI) y qué herramienta aplicar en cada caso."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Contract testing: estrategia

## Cuándo aplicar y cuándo no
- Aplica cuando dos componentes desplegables independientes se comunican por HTTP, gRPC o mensajes y pueden evolucionar a ritmos distintos.
- No aplica dentro de un mismo módulo o monolito desplegado a la vez: bastan tests de integración.
- Este skill es la estrategia; la herramienta consumer-driven concreta está en `contract-testing-pact`.

## Reglas
- **MUST** tener un contrato explícito y versionado por cada interfaz entre servicios: OpenAPI (REST), AsyncAPI/schema registry (eventos), `.proto` (gRPC).
- **MUST** verificar el contrato en CI en ambos lados: el proveedor demuestra que lo cumple; el consumidor demuestra qué usa.
- **MUST** elegir enfoque por caso: consumer-driven (Pact) cuando hay varios consumidores con necesidades distintas; schema-first con validación cuando el proveedor publica un contrato único.
- **MUST** que un cambio incompatible falle en el pipeline del proveedor antes de desplegar (ver `backward-compatibility-rules`).
- **SHOULD** que los stubs de consumidor (WireMock) se generen del contrato, no se escriban a mano.
- **SHOULD** probar eventos con compatibilidad de esquema (ver `schema-registry-and-evolution`).
- **MUST NOT** sustituir los contract tests por un E2E entre entornos compartidos.
- **MUST NOT** probar lógica de negocio en el contract test: solo forma, tipos y semántica de la interfaz.

## Por qué
Sin contrato verificado, la incompatibilidad se descubre en integración o en producción. Los contract tests dan feedback en el PR de cada equipo, sin levantar todos los servicios.

## Ejemplos
### Mal
```text
Equipo A cambia "total" de number a string. Los tests de A pasan (stub propio).
El servicio B falla en producción al deserializar.
```
### Bien
```text
Proveedor (orders): verifica en CI su OpenAPI y el pact de cada consumidor.
Consumidor (billing): su test genera pact con GET /orders/{id} usando solo
  los campos id, total, currency.
Pipeline del proveedor bloquea el merge si rompe algún pact publicado.
```
```yaml
# Ejemplo de decisión en la ficha del servicio
interfaces:
  - name: orders-api
    style: rest
    contract: openapi
    verification: pact-provider
  - name: order-events
    style: async
    contract: asyncapi
    verification: schema-compat
```

## Criterios de decisión y trampas
### Cómo decidir
- Consumer-driven (Pact) cuando hay pocos consumidores conocidos; contrato del proveedor (OpenAPI) y validación cuando los consumidores son muchos o desconocidos; esquemas con reglas de compatibilidad para eventos.
- `can-i-deploy` o equivalente como puerta antes de desplegar.
### Trampas frecuentes
- Contratos que copian toda la respuesta real y rompen con cualquier cambio.
- Verificación del proveedor que stubbea la lógica que debería probar.
- No publicar los resultados de verificación al broker.
- Contratos sin versionar.
- Mezclar contrato con pruebas funcionales.
### Evidencia
- El pipeline del proveedor falla ante un cambio incompatible antes de desplegar.

## Checklist de revisión
- [ ] Cada interfaz entre servicios tiene contrato versionado.
- [ ] El pipeline del proveedor ejecuta la verificación de contratos.
- [ ] Los cambios incompatibles se detectan antes del merge.
- [ ] Sin lógica de negocio dentro del contract test.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Verificación del proveedor en CI | 1 | pipeline del proyecto generado (pendiente) |
| Compatibilidad de esquemas de eventos | 1 | skill `schema-registry-and-evolution` |
| Revisión de la decisión de enfoque | 4 | revisión humana / ADR del servicio |

## Relacionados, fuentes y mantenimiento
- Relacionados: `contract-testing-pact`, `openapi-contract-first`, `asyncapi-event-contracts`, `backward-compatibility-rules`, `wiremock-and-stubbing`.
- Fuentes: documentación oficial de Pact (https://docs.pact.io).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
