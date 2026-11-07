---
name: graphql
description: "Usar al exponer o consumir una API GraphQL (Spring for GraphQL): esquema, N+1, límites de consulta, errores y autorización."
metadata:
  block: "06-api-and-integration"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# GraphQL

## Cuándo aplicar y cuándo no
- Aplica cuando hay clientes con necesidades de datos muy variables (BFF, front-end rico) y se decide GraphQL en un ADR.
- No aplica a integraciones servicio-a-servicio simples (REST o gRPC) ni como sustituto de un diseño de dominio pobre.

## Reglas
- **MUST** escribir primero el esquema (`.graphqls`, schema-first) y revisarlo como contrato.
- **MUST** resolver relaciones con `@BatchMapping` o DataLoader para evitar N+1 (ver `n-plus-one`).
- **MUST** limitar profundidad y complejidad de consulta y tamaño de página; **MUST NOT** permitir consultas sin cota.
- **MUST** desactivar introspección en entornos expuestos a terceros salvo necesidad documentada.
- **MUST** autorizar en cada resolver/campo sensible (`@PreAuthorize` o equivalente), no solo en el endpoint `/graphql`.
- **MUST** usar paginación por conexiones/cursor para listas (`pagination-filter-sort`).
- **MUST NOT** filtrar excepciones internas en `errors[]`; mapear a errores con `extensions.code` estable.
- **SHOULD** evolucionar con `@deprecated(reason:)` en lugar de versiones; añadir campos nunca rompe, quitarlos sí.
- **SHOULD** usar mutaciones con un único argumento `input` y un payload con errores de negocio tipados.

## Por qué
GraphQL traslada el control de la forma de la consulta al cliente: sin límites de coste una sola consulta anidada puede tumbar la base de datos, y la autorización por endpoint deja campos expuestos.

## Ejemplos
### Mal
```graphql
type Query { orders: [Order] }                       # sin paginación
type Order { id: ID  customer: Customer }
```
```java
@SchemaMapping List<Order> customer(Order o) { return repo.findByCustomer(o.customerId()); } // N+1
```
### Bien
```graphql
type Query { orders(first: Int = 20, after: String): OrderConnection! }
type Order { id: ID!  customer: Customer! @deprecated(reason: "usar customerRef") }
```
```java
@BatchMapping
Map<Order, Customer> customer(List<Order> orders) {
    var byId = customerRepo.findAllById(orders.stream().map(Order::customerId).toList())
        .stream().collect(Collectors.toMap(Customer::id, c -> c));
    return orders.stream().collect(Collectors.toMap(o -> o, o -> byId.get(o.customerId())));
}
```
Límite de profundidad: registrar instrumentación de max depth/complexity de graphql-java (TODO-VERIFY nombres de clase por versión).

## Checklist de revisión
- [ ] Esquema revisado antes del código; listas paginadas.
- [ ] Relaciones con batch/DataLoader.
- [ ] Profundidad/complejidad limitadas; introspección decidida.
- [ ] Autorización a nivel de campo/resolver.
- [ ] Errores con códigos estables, sin detalles internos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Test del proyecto: consulta profunda es rechazada | 1 | pendiente: se genera con el proyecto |
| Revisión del esquema y resolvers | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `n-plus-one`, `pagination-filter-sort`, `authz-rbac-abac-rebac`, `backward-compatibility-rules`.
- Fuentes: spec graphql.org, documentación de Spring for GraphQL — TODO-VERIFY versión y APIs de instrumentación, no consultadas el 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
