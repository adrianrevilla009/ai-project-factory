---
name: code-smells-and-refactoring
description: Usar al revisar código con olores (métodos largos, clases dios, duplicación) y al refactorizar con seguridad.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Code smells y refactorización

## Cuándo aplicar y cuándo no
- Aplica al revisar PRs, al tocar código difícil de entender y antes de añadir una funcionalidad sobre código frágil.
- No aplica a código a punto de eliminarse ni a refactors masivos sin cobertura de tests ni objetivo.

## Reglas
- **MUST** tener tests que pasan (caracterización si faltan) antes de refactorizar.
- **MUST** hacer refactors en pasos pequeños, con tests en verde entre pasos, separados de los cambios de comportamiento (commits distintos).
- **MUST** tratar como olores a corregir: método largo, clase dios, parámetros en cascada, `Feature Envy`, duplicación, primitive obsession, switch sobre tipo, comentarios que explican código confuso.
- **SHOULD** aplicar la regla de los scouts: dejar el código tocado un poco mejor, con alcance acotado.
- **SHOULD** refactorizar con las herramientas del IDE (extract method, rename) antes que a mano.
- **MUST NOT** mezclar refactor y funcionalidad en el mismo commit.
- **MUST NOT** "arreglar" olores mediante supresiones de análisis estático sin justificar.
- **SHOULD** registrar olores no abordables como deuda (`tech-debt-management`).

## Por qué
El código se lee más de lo que se escribe; los olores son síntomas de coste de cambio creciente. Refactorizar sin red de tests es reescribir a ciegas. Separar refactor y comportamiento hace revisables los diffs y permite revertir con precisión.

## Ejemplos
### Mal
```java
Money calc(Order o, boolean vip, boolean eu, String coupon, int year) {   // parámetros en cascada
    Money t = Money.ZERO;
    for (Line l : o.lines()) t = t.plus(l.price().times(l.qty()));
    if (vip) t = t.times(0.9);
    if (eu) t = t.plus(t.times(0.21));
    // ... 80 líneas más
    return t;
}
```
### Bien
```java
Money total(Order order, PricingContext ctx) {
    Money subtotal = order.subtotal();
    Money discounted = ctx.discounts().apply(subtotal);
    return ctx.taxes().apply(discounted);
}
// Pasos: test de caracterización -> extract method subtotal() -> introduce parameter object PricingContext
```

## Checklist de revisión
- [ ] Hay tests antes del refactor.
- [ ] Commits de refactor separados de los de comportamiento.
- [ ] Métodos cortos con un único nivel de abstracción.
- [ ] No se suprimen avisos de análisis estático para ocultar el olor.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Análisis estático (PMD/Checkstyle: complejidad y longitud) | 1 | `static-analysis` (bloque 08); configuración en el proyecto generado, pendiente |
| Revisión de PR (olores y separación de commits) | 3 | agente de revisión de código (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `solid`, `tech-debt-management`, `static-analysis`, `tdd`.
- Fuentes: Martin Fowler, "Refactoring", 2ª ed. (2018); catálogo en refactoring.com — TODO-VERIFY.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
