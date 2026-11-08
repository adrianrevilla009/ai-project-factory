---
name: property-based-testing
description: "Usar al testear invariantes, parsers, serialización o reglas con muchos casos límite con jqwik (propiedades y generadores) en vez de ejemplos fijos."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Property-based testing con jqwik

## Cuándo aplicar y cuándo no
- Aplica a funciones puras con invariantes claros: round-trip serialización, idempotencia, orden, cálculos monetarios, validadores, parsers.
- No aplica a código con efectos externos (BD, red) ni cuando no se sabe formular la propiedad: usar tests por ejemplo.

## Reglas
- **MUST** formular la propiedad como invariante (ej. `decode(encode(x)) == x`), no como reimplementación de la función.
- **MUST** que el test sea reproducible: conservar la semilla que jqwik reporta al fallar y convertir el contraejemplo en un test por ejemplo.
- **MUST** acotar generadores al dominio válido (`@IntRange`, `@StringLength`, `Arbitraries`) en vez de filtrar con `assume` masivamente.
- **MUST NOT** usar aleatoriedad no controlada (`Math.random`, `UUID.randomUUID`) dentro de la propiedad.
- **SHOULD** complementar, no sustituir, los tests por ejemplo de casos de negocio conocidos.
- **SHOULD** mantener el número de intentos por defecto en CI local y subirlo solo en el job nocturno.
- **SHOULD** crear generadores reutilizables (`@Provide`) para tipos de dominio como `Money`.

## Por qué
Los ejemplos prueban lo que el autor imagina; los generadores encuentran el desbordamiento, el vacío o el Unicode que nadie pensó. El encogimiento (shrinking) entrega el contraejemplo mínimo.

## Ejemplos
### Mal
```java
@Test
void sumsTwoAmounts() {
    assertThat(Money.of("1.00").plus(Money.of("2.00"))).isEqualTo(Money.of("3.00")); // un solo caso
}
```
### Bien
```java
class MoneyProperties {
    @Property
    void additionIsCommutative(@ForAll("amounts") Money a, @ForAll("amounts") Money b) {
        assertThat(a.plus(b)).isEqualTo(b.plus(a));
    }

    @Property
    void serializationRoundTrip(@ForAll("amounts") Money m) {
        assertThat(Money.parse(m.format())).isEqualTo(m);
    }

    @Provide
    Arbitrary<Money> amounts() {
        return Arbitraries.bigDecimals().between(BigDecimal.ZERO, new BigDecimal("1000000"))
                .ofScale(2).map(Money::of);
    }
}
```
Dependencia `net.jqwik:jqwik` en scope test, versión en el BOM (comprobar versión y compatibilidad con la versión de JUnit Platform).

## Checklist de revisión
- [ ] La propiedad expresa un invariante, no copia la implementación.
- [ ] Generadores acotados al dominio; sin abuso de `assume`.
- [ ] Contraejemplos antiguos convertidos en tests por ejemplo.
- [ ] Sin aleatoriedad externa a jqwik.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana / agente de tests de la formulación de propiedades | 3 | `.claude/agents/quality/test-automation.md` |
| Los tests corren en el build Maven del proyecto generado | 1 | `mvn test` (hook `require_green_tests`) en `.claude/hooks/stop/require_green_tests.py` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `unit-testing-java`, `mutation-testing`, `time-and-money`, `test-data-management`.
- Fuentes: https://jqwik.net/docs/current/user-guide.html (comprobar anotaciones y versión, no contrastadas a 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
