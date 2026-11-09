---
name: solid
description: Usar al diseñar o revisar clases Java (responsabilidades, extensión, sustitución, interfaces e inversión de dependencias).
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Principios SOLID

## Cuándo aplicar y cuándo no
- Aplica al diseñar clases y módulos de dominio/aplicación y al revisar PRs con clases grandes o jerarquías de herencia.
- No aplica como dogma a código trivial, DTOs ni scripts: sin presión de cambio, no hay que abstraer.

## Reglas
- **MUST** (SRP) que una clase tenga una sola razón para cambiar; separar reglas de negocio, persistencia y formato.
- **SHOULD** (OCP) extender comportamiento con composición/estrategias donde ya haya variación real, no por anticipación.
- **MUST** (LSP) que una subclase respete el contrato de la base (precondiciones no más fuertes, postcondiciones no más débiles); si lanza `UnsupportedOperationException`, el diseño es erróneo.
- **MUST** (ISP) interfaces pequeñas orientadas al cliente; no obligar a implementar métodos sin uso.
- **MUST** (DIP) depender de abstracciones en la frontera del dominio y usar inyección por constructor.
- **SHOULD** preferir composición sobre herencia.
- **MUST NOT** crear una interfaz por cada clase si solo hay una implementación y no es una frontera.
- **MUST NOT** usar inyección por campo (`@Autowired` en atributos); constructor explícito, sin Lombok (D27).

## Por qué
SOLID reduce el coste de cambio cuando hay variación real. Aplicado sin criterio genera capas vacías y abstracciones prematuras. La regla práctica: abstraer en las fronteras y ante dos variantes reales, no antes.

## Ejemplos
### Mal
```java
class ReportService {                        // SRP: consulta, calcula, formatea y envía
    void run() { /* SQL */ /* cálculo */ /* CSV */ /* SMTP */ }
}
class Penguin extends Bird { void fly() { throw new UnsupportedOperationException(); } } // LSP
```
### Bien
```java
interface DiscountPolicy { Money discount(Order order); }
final class SeasonalDiscount implements DiscountPolicy { ... }
final class LoyaltyDiscount implements DiscountPolicy { ... }

final class PriceCalculator {
    private final List<DiscountPolicy> policies;
    PriceCalculator(List<DiscountPolicy> policies) { this.policies = List.copyOf(policies); }
    Money total(Order o) {
        Money d = policies.stream().map(p -> p.discount(o)).reduce(Money.ZERO, Money::plus);
        return o.subtotal().minus(d);
    }
}
```

## Checklist de revisión
- [ ] Cada clase se describe sin usar "y".
- [ ] No hay subclases que rechacen métodos heredados.
- [ ] Las interfaces son pequeñas y tienen más de un motivo de existir.
- [ ] Dependencias por constructor, sin inyección por campo.
- [ ] No hay abstracciones sin segunda variante ni frontera.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de PR por agente/humano; los principios no son comprobables al 100% | 3 | agente de revisión de código (pendiente) |
| Inyección por campo prohibida | 1 | regla ArchUnit `NO_CLASSES_SHOULD_USE_FIELD_INJECTION` de ArchUnit; pendiente de añadir a `policies/archunit/` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `clean-architecture`, `hexagonal`, `gof-patterns-in-practice`, `code-smells-and-refactoring`.
- Fuentes: Robert C. Martin, "Agile Software Development: Principles, Patterns, and Practices" (2002).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
