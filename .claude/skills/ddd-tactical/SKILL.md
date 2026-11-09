---
name: ddd-tactical
description: "Usar al modelar el dominio dentro de un bounded context: entidades, value objects, aggregates, repositorios y servicios de dominio."
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "archunit"
---

# DDD táctico

## Cuándo aplicar y cuándo no
- Aplica al implementar lógica de negocio no trivial dentro de un bounded context (Java + Spring Boot, sin Lombok).
- No aplica a módulos puramente CRUD o de reporting; usar proyecciones simples (ver `cqrs`).

## Reglas
- **MUST** modelar un aggregate con una única raíz; todo cambio pasa por métodos de la raíz que protegen invariantes.
- **MUST** referenciar otros aggregates solo por identidad (`CustomerId`), nunca por referencia de objeto.
- **MUST** modificar un solo aggregate por transacción; la coordinación entre aggregates va por eventos de dominio (ver `event-driven`, `sagas-and-process-managers`).
- **MUST** usar value objects inmutables (records Java) para conceptos sin identidad: `Money`, `Email`, `Quantity`.
- **MUST NOT** exponer setters públicos en entidades; los estados se cambian con verbos del lenguaje ubicuo.
- **MUST NOT** depender de Spring, JPA ni de infraestructura desde el paquete `domain`.
- **MUST NOT** usar Lombok (D27); usar records y código explícito.
- **SHOULD** definir un repositorio por aggregate root, con interfaz en `domain` e implementación en `infrastructure`.
- **SHOULD** mantener aggregates pequeños; si una colección crece sin límite, es otro aggregate.
- **SHOULD** usar servicios de dominio solo cuando la lógica no pertenece a ninguna entidad.

## Por qué
Los aggregates definen fronteras de consistencia transaccional. Aggregates grandes causan contención y bloqueos; referencias por objeto filtran cargas perezosas y rompen los límites. Un dominio anémico (entidades con getters/setters y lógica en servicios) dispersa las invariantes y las hace imposibles de garantizar.

## Ejemplos
### Mal
```java
public class Order {
    private Customer customer;            // referencia directa a otro aggregate
    private List<OrderLine> lines;
    public void setStatus(String status) { this.status = status; } // sin invariantes
}
```
### Bien
```java
public record Money(java.math.BigDecimal amount, String currency) {
    public Money {
        if (amount.signum() < 0) throw new IllegalArgumentException("negative amount");
    }
}

public class Order {                      // aggregate root
    private final OrderId id;
    private final CustomerId customerId;  // por identidad
    private final List<OrderLine> lines = new java.util.ArrayList<>();
    private OrderStatus status = OrderStatus.DRAFT;

    public void addLine(ProductId product, int quantity, Money unitPrice) {
        if (status != OrderStatus.DRAFT) throw new IllegalStateException("order not editable");
        if (quantity <= 0) throw new IllegalArgumentException("quantity must be positive");
        lines.add(new OrderLine(product, quantity, unitPrice));
    }

    public void place() {
        if (lines.isEmpty()) throw new IllegalStateException("empty order");
        status = OrderStatus.PLACED;      // registra OrderPlaced para publicarlo tras el commit
    }
}
```

## Checklist de revisión
- [ ] Cada aggregate tiene una raíz y sus invariantes viven en ella.
- [ ] Referencias entre aggregates por id.
- [ ] Una transacción modifica un solo aggregate.
- [ ] El paquete `domain` no importa `org.springframework` ni `jakarta.persistence`.
- [ ] Value objects inmutables; sin Lombok.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: `domain` no depende de Spring/JPA | 1 | `policies/archunit/DomainIsolationRules.java` (ejemplo, no ejecutado) |
| Revisión de aggregates y fronteras transaccionales | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `ddd-strategic`, `hexagonal`, `layering-rules-archunit`, `event-driven`, `cqrs`.
- Fuentes: Evans (2003); Vernon, "Effective Aggregate Design" (2011).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
