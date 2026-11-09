---
name: backward-compatibility-rules
description: Usar al modificar cualquier contrato (OpenAPI, Protobuf, GraphQL, eventos) para decidir si el cambio es compatible o rompiente.
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Reglas de compatibilidad hacia atrás

## Cuándo aplicar y cuándo no
- Aplica a todo cambio en un contrato con consumidores fuera del módulo que lo define.
- No aplica a contratos aún no publicados (primer despliegue) ni a código interno sin consumidores externos.

## Reglas
- **MUST** tratar como compatible: añadir campo opcional en respuesta, añadir endpoint, añadir valor opcional de petición, añadir RPC o campo Protobuf nuevo (número nuevo).
- **MUST** tratar como rompiente: quitar/renombrar campo o ruta, cambiar tipo o formato, volver obligatorio un campo, estrechar un enum de petición, cambiar semántica, cambiar código de estado de éxito.
- **MUST** exigir a los consumidores tolerar campos desconocidos (tolerant reader): `FAIL_ON_UNKNOWN_PROPERTIES=false` en Jackson (`spring.jackson.deserialization.fail-on-unknown-properties=false`, verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08).
- **MUST** ampliar un enum de respuesta solo si el contrato documenta que los clientes deben manejar valores desconocidos.
- **MUST** migrar con expand/contract: añadir lo nuevo, migrar consumidores, retirar lo viejo en una versión posterior (`api-versioning-deprecation`).
- **MUST** ejecutar un diff automático del contrato contra la rama principal en CI y bloquear rompientes sin versión mayor nueva.
- **MUST NOT** reutilizar nombres o números retirados con otro significado.
- **SHOULD** registrar cada excepción rompiente aprobada en un ADR.

## Por qué
Productores y consumidores se despliegan de forma independiente: un cambio "pequeño" que rompe a un solo consumidor produce incidentes que el productor no ve en sus tests. La regla del lector tolerante y expand/contract permiten desplegar sin coordinación.

## Ejemplos
### Mal
```yaml
# v1 -> v1: 'total' pasa de number a string y 'customerId' se vuelve required
Order:
  required: [id, customerId]
  properties: { total: { type: string } }
```
### Bien
```yaml
# v1 (compatible): se añade campo opcional y se mantiene el anterior
Order:
  required: [id]
  properties:
    total: { type: number, deprecated: true }
    totalAmount: { type: string, description: "Decimal en texto; sustituye a total" }
```
```text
# Chequeo en CI (ejemplo; confirmar herramienta y sintaxis en su documentación)
openapi-diff old.yaml new.yaml        # OpenAPI
buf breaking --against '.git#branch=main'   # Protobuf
```

## Checklist de revisión
- [ ] El cambio está clasificado (compatible / rompiente).
- [ ] Consumidores toleran campos desconocidos.
- [ ] Cambios rompientes llevan versión nueva y plan expand/contract.
- [ ] El diff automático de contrato corre en CI.
- [ ] Sin reutilización de nombres/números retirados.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Diff de OpenAPI / `buf breaking` / compatibilidad de esquema en CI | 1 | pendiente: pipeline del proyecto generado; la fábrica no lo contiene |
| Aprobación humana de excepciones rompientes | 4 | revisión humana (ADR) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `api-versioning-deprecation`, `openapi-contract-first`, `grpc-protobuf`, `asyncapi-event-contracts`, `schema-registry-and-evolution`, `contract-testing-pact`.
- Fuentes: patrón Tolerant Reader (Fowler), documentación de buf y de herramientas de diff OpenAPI.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
