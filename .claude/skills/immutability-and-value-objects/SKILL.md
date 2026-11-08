---
name: immutability-and-value-objects
description: Usar al diseñar clases de datos, DTOs, eventos o value objects para hacerlos inmutables, con copias defensivas e invariantes validadas en el constructor.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Inmutabilidad y value objects

## Cuándo aplicar y cuándo no
- Aplica a DTOs, eventos, comandos, identificadores de dominio, importes y cualquier objeto compartido entre hilos o cacheado.
- No aplica a entidades JPA (requieren constructor sin argumentos y estado mutable gestionado por el proveedor; ver `jpa-entity-design`) ni a buffers de rendimiento local.

## Reglas
- **MUST** modelar value objects (`Email`, `OrderId`, `Money`) como `record` o clase `final` con campos `final`.
- **MUST** validar invariantes en el constructor canónico del record; no debe existir una instancia inválida.
- **MUST** hacer copia defensiva de colecciones recibidas: `List.copyOf(items)` en el constructor.
- **MUST NOT** exponer colecciones mutables; devolver vistas inmutables o copias.
- **MUST NOT** usar `String` o `long` desnudos para identificadores de dominio distintos (primitive obsession): un `CustomerId` no es un `OrderId`.
- **SHOULD** usar métodos `withX(...)` que devuelven una copia nueva en lugar de setters.
- **SHOULD** marcar las clases como `final` salvo diseño explícito para herencia.
- **MUST NOT** usar `Date` ni arrays mutables como campos de un value object sin copiarlos.

## Por qué
Un objeto inmutable es seguro entre hilos sin sincronización, puede usarse como clave de mapa y no cambia bajo los pies de quien lo recibió. Un record con `List<String>` sin copia defensiva *parece* inmutable pero el llamante conserva la referencia y lo muta. Validar en el constructor evita estados inválidos viajando por el sistema.

## Ejemplos
### Mal
```java
public class Order {
    private final List<String> items;
    public Order(List<String> items) { this.items = items; }   // aliasing
    public List<String> getItems() { return items; }           // expone mutable
}
String customerId = order.id(); // ¿es id de cliente o de pedido?
```
### Bien
```java
public record CustomerId(String value) {
    public CustomerId {
        if (value == null || value.isBlank()) {
            throw new IllegalArgumentException("customerId must not be blank");
        }
    }
}

public record Order(CustomerId customerId, List<String> items) {
    public Order {
        Objects.requireNonNull(customerId, "customerId");
        items = List.copyOf(items); // copia inmutable; rechaza nulls
        if (items.isEmpty()) throw new IllegalArgumentException("items must not be empty");
    }
    public Order withItem(String item) {
        var next = new ArrayList<>(items);
        next.add(item);
        return new Order(customerId, next);
    }
}
```

## Checklist de revisión
- [ ] Campos `final`, sin setters en objetos de valor.
- [ ] Colecciones copiadas al entrar y no expuestas mutables al salir.
- [ ] Invariantes validadas en el constructor.
- [ ] Identificadores de dominio con tipo propio.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de diseño de tipos | 3 | agente `code-reviewer` (pendiente de definir) |
| Regla ArchUnit "los records/VO del paquete `domain` no tienen setters" | 1 | `policies/archunit/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `modern-java-idioms`, `equals-hashcode-tostring`, `time-and-money`, `jpa-entity-design`.
- Fuentes: Effective Java (Bloch), ítem sobre inmutabilidad (libro, no verificado en línea); JEP 395 (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
