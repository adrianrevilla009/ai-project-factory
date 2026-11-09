---
name: tdd
description: "Usar al implementar lógica de dominio o corregir un bug: ciclo rojo-verde-refactor con tests primero y pasos pequeños."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# TDD (rojo, verde, refactor)

## Cuándo aplicar y cuándo no
- Aplica a reglas de negocio, cálculos, validaciones y a cualquier corrección de bug (test que reproduce el fallo primero).
- No aplica a exploración/spikes descartables ni a código de pegamento trivial (configuración, DTOs sin lógica); en esos casos se escribe el test justo después.

## Reglas
- **MUST** escribir un test que falla (rojo) por la razón correcta antes de escribir código de producción.
- **MUST** ejecutar el test y ver el fallo; un test nunca visto fallar no prueba nada.
- **MUST** escribir el mínimo código para pasar (verde) y refactorizar solo con todo en verde.
- **MUST** que todo bug corregido incluya un test de regresión que falla antes del arreglo.
- **SHOULD** avanzar en pasos pequeños: un comportamiento por test, nombre que describe el comportamiento.
- **SHOULD** empezar por el caso más simple y añadir casos límite después (null, vacío, límites, duplicados).
- **MUST NOT** modificar el test para que pase cuando el fallo revela un defecto del código.
- **MUST NOT** probar detalles de implementación (métodos privados, orden interno de llamadas) en vez de comportamiento observable.

## Por qué
Escribir el test primero obliga a diseñar la API desde el uso, produce código testeable por construcción y deja una red de seguridad para refactorizar. El paso rojo valida el propio test. En trabajo con agentes, evita que se generen tests que solo reflejan el código recién escrito.

## Ejemplos
### Mal
```java
// Código escrito primero; el test se deduce de él y siempre pasa.
@Test
void calculate() {
    assertThat(service.calculate(order)).isEqualTo(service.calculate(order));
}
```
### Bien
```java
// 1) ROJO: no existe aún DiscountPolicy.discountFor
@Test
void ordersOver100Eur_get10PercentDiscount() {
    var policy = new DiscountPolicy();
    assertThat(policy.discountFor(Money.eur("150.00"))).isEqualTo(Money.eur("15.00"));
}

@Test
void ordersAtOrBelow100Eur_getNoDiscount() {
    assertThat(new DiscountPolicy().discountFor(Money.eur("100.00"))).isEqualTo(Money.eur("0.00"));
}
// 2) VERDE: implementación mínima  3) REFACTOR con tests en verde
```

## Criterios de decisión y trampas
### Cómo decidir
- TDD estricto en lógica de dominio y reglas con casos límite, donde el diseño se beneficia del ciclo.
- En exploración o spikes, escribe primero el código y tíralo; luego rehazlo con tests.
- En código muy dependiente del framework (controladores, configuración), prueba el comportamiento en la capa de aplicación en vez de forzar TDD sobre el pegamento.
### Trampas frecuentes
- Tests acoplados a la implementación (mocks de colaboradores internos) que impiden refactorizar.
- Pasos demasiado grandes: un test que exige media funcionalidad.
- No ver fallar el test, o verlo fallar por una razón equivocada.
- Refactorizar con tests en rojo.
- Confundir TDD con alta cobertura.
### Evidencia
- Todo bug corregido trae un test que falla en el commit anterior y pasa en el del arreglo.

## Checklist de revisión
- [ ] Los tests nuevos fallaron antes de la implementación (evidencia en la sesión o el historial).
- [ ] Cada bug corregido trae su test de regresión.
- [ ] Los nombres describen comportamiento, no métodos.
- [ ] Ningún test fue debilitado para pasar.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook que exige tests verdes al parar | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Mutation testing detecta tests que no verifican nada | 2 | skill `mutation-testing` (pendiente de escribir) |
| Revisión de que el test precede al código | 4 | revisión humana / `code-reviewer` |

El orden test-primero no es comprobable por script de forma fiable: es revisión humana.

## Relacionados, fuentes y mantenimiento
- Relacionados: `unit-testing-java`, `bdd`, `mutation-testing`, `code-smells-and-refactoring`.
- Fuentes: Kent Beck, *Test-Driven Development: By Example* (libro; sin URL verificada).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
