---
name: projections-and-dtos
description: Usar al diseñar lecturas, listados o informes para decidir entre entidad, proyección Spring Data o DTO.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Proyecciones y DTOs

## Cuándo aplicar y cuándo no
- Aplica a consultas de solo lectura: listados, búsquedas, informes, endpoints GET.
- No aplica a casos de uso que modifican la entidad (ahí se carga la entidad gestionada).

## Reglas
- **MUST** usar proyección (record/interfaz/constructor expression) para lecturas que no modifican datos.
- **MUST NOT** cargar entidades completas para devolver 3 columnas.
- **SHOULD** usar `record` como DTO de proyección con constructor expression en JPQL: `select new ...`.
- **SHOULD** preferir proyecciones de clase (records) a proyecciones de interfaz dinámicas cuando el rendimiento importe; las de interfaz anidadas pueden cargar la entidad completa.
- **MUST NOT** devolver entidades JPA desde controladores.
- **MUST** nombrar el DTO por caso de uso (`OrderSummary`), no por tabla.
- **SHOULD** usar proyecciones también para evitar N+1 en listados con datos de varias tablas.
- **MUST NOT** reutilizar un único DTO "gordo" para todos los casos de uso.

## Por qué
Una entidad gestionada arrastra dirty checking, proxies y asociaciones; una proyección es un SELECT de solo las columnas necesarias, sin estado en el contexto de persistencia. Reduce memoria, ancho de banda y riesgo de N+1.

## Ejemplos
### Mal
```java
List<Order> orders = orderRepository.findAll();           // entidad completa
return orders.stream()
    .map(o -> new OrderRow(o.getId(), o.getCustomer().getName())) // N+1
    .toList();
```
### Bien
```java
public record OrderSummary(Long id, String customerName, BigDecimal total) { }

interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("""
        select new com.acme.orders.OrderSummary(o.id, c.name, o.total)
        from Order o join o.customer c
        where o.status = :status
        """)
    List<OrderSummary> findSummariesByStatus(OrderStatus status);
}
```

## Checklist de revisión
- [ ] Los GET de listado devuelven DTOs, no entidades.
- [ ] La consulta selecciona solo las columnas necesarias.
- [ ] Un DTO por caso de uso.
- [ ] Sin entidades en la firma de controladores.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: controllers no dependen de `@Entity` | 1 | pendiente (`policies/archunit/`) |
| Test de conteo de sentencias | 1 | tests del proyecto generado |
| Revisión de consultas de lectura | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `n-plus-one`, `query-strategy`, `mapping-mapstruct`, `pagination`.
- Fuentes: Spring Data JPA reference (Projections).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
