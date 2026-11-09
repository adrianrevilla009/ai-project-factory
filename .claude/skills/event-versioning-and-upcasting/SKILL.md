---
name: event-versioning-and-upcasting
description: "Usar al cambiar la forma de un evento almacenado: versionado de esquema, upcasters, cambios compatibles y qué no hacer con eventos inmutables; subskill de event-sourcing."
metadata:
  block: "22-polyglot-persistence"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "review"
---

# Versionado de eventos y upcasting

## Cuándo aplicar y cuándo no
- Aplica a cualquier cambio en el payload de un evento ya persistido o publicado.
- No aplica a eventos que aún no salieron de desarrollo local. Subskill de `event-sourcing`.

## Reglas
- **MUST** guardar `type` y `schemaVersion` en cada evento.
- **MUST** preferir cambios compatibles: añadir campos opcionales con valor por defecto; no cambiar significado ni tipo de un campo existente.
- **MUST** para cambios incompatibles crear una versión nueva (`OrderPlacedV2`) y un upcaster `V1 -> V2` que se aplique al leer.
- **MUST** encadenar upcasters (`V1->V2->V3`); el dominio solo ve la última versión.
- **MUST** cubrir cada upcaster con un test usando un payload real de la versión antigua (fixture congelado).
- **MUST NOT** reescribir ni migrar masivamente los eventos almacenados para "limpiar" versiones (rompe inmutabilidad y auditoría); si un cambio de almacén lo exige, hacerlo como nueva copia verificable.
- **MUST NOT** borrar o renombrar un tipo de evento mientras existan streams que lo contienen.
- **SHOULD** registrar en el esquema (`schema-registry-and-evolution`) las versiones y su compatibilidad.
- **SHOULD** mantener upcasters puros y sin I/O; si falta un dato, usar un valor por defecto explícito y documentado.

## Por qué
Un event store vive años: el código nuevo debe leer eventos escritos hace tiempo. Upcastear al leer conserva la historia intacta y confina la complejidad en un punto testeable.

## Ejemplos
### Mal
```java
// Se cambia el tipo del campo y se rompen los eventos antiguos
public record OrderPlaced(String orderId, String customerId, BigDecimal total) {} // antes: long totalCents
```
### Bien
```java
public record OrderPlacedV1(String orderId, String customerId, long totalCents) {}
public record OrderPlacedV2(String orderId, String customerId, long totalCents, String currency) {}

public final class OrderPlacedUpcasterV1ToV2 implements Upcaster<OrderPlacedV1, OrderPlacedV2> {
    @Override public OrderPlacedV2 upcast(OrderPlacedV1 old) {
        return new OrderPlacedV2(old.orderId(), old.customerId(), old.totalCents(), "EUR"); // por defecto documentado en ADR
    }
}

@Test
void upcastsFrozenV1Fixture() throws Exception {
    var v1 = mapper.readValue(Files.readString(Path.of("src/test/resources/events/order-placed-v1.json")), OrderPlacedV1.class);
    assertThat(new OrderPlacedUpcasterV1ToV2().upcast(v1).currency()).isEqualTo("EUR");
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Los eventos publicados no cambian: evoluciona con versiones y conversores (upcasters) que traducen eventos antiguos al formato actual al leer.
- Cambios compatibles (añadir opcionales) sin versión nueva.
### Trampas frecuentes
- Modificar eventos ya guardados.
- Conversores sin pruebas con eventos reales antiguos.
- Eliminar la versión antigua del código.
- Cambiar el significado sin cambiar de tipo.
- Una cadena de conversores tan larga que nadie la entiende.
### Evidencia
- Pruebas que leen eventos de cada versión histórica y producen el estado correcto.

## Checklist de revisión
- [ ] Cada evento persistido lleva `schemaVersion`.
- [ ] Cambio compatible o upcaster con test sobre fixture antiguo.
- [ ] Ningún script modifica eventos ya escritos.
- [ ] Los valores por defecto de upcasting están justificados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de fixtures congelados por versión (lo incluye el proyecto generado) | 1 | tests del proyecto generado |
| Comprobación de compatibilidad en el registro de esquemas | 1 | pendiente (`schema-registry-and-evolution`) |
| Revisión de cambios en clases de evento | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `event-sourcing`, `aggregates-and-event-design`, `schema-registry-and-evolution`, `backward-compatibility-rules`, `testing-event-sourced-systems`.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
