---
name: bdd
description: "Usar al convertir criterios de aceptación en escenarios Given/When/Then ejecutables (Cucumber u homólogo) o al decidir si BDD aporta valor."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# BDD (comportamiento como especificación)

## Cuándo aplicar y cuándo no
- Aplica a flujos de negocio con reglas que producto o negocio deben poder leer y validar (alta de pedido, aprobaciones, cálculo de tarifas).
- No aplica a lógica técnica (mapeos, adaptadores, utilidades): ahí basta un test JUnit con nombre descriptivo.
- Si nadie de negocio lee los `.feature`, BDD es solo una capa extra de indirección: usar JUnit.

## Reglas
- **MUST** redactar escenarios en lenguaje de dominio (Given/When/Then), sin detalles de UI, SQL ni HTTP.
- **MUST** un escenario = un comportamiento, con datos mínimos y explícitos en el propio escenario.
- **MUST** que los escenarios sean independientes y deterministas (sin orden entre ellos).
- **SHOULD** ejecutarlos contra la capa de aplicación o API, no a través de navegador, salvo recorridos críticos (ver `e2e-testing`).
- **SHOULD** usar `Scenario Outline` solo para variaciones de datos de la misma regla.
- **SHOULD** que los step definitions sean finos y deleguen en un helper de dominio; sin lógica de negocio en ellos.
- **MUST NOT** reutilizar steps con estado compartido global entre escenarios.
- **MUST NOT** convertir cada test unitario en un `.feature`.

## Por qué
Los escenarios sirven de documentación viva y de puente con negocio; su valor desaparece si se escriben como guiones técnicos. Mantener pocos escenarios, legibles y de comportamiento evita una suite lenta y costosa de mantener.

## Ejemplos
### Mal
```gherkin
Scenario: test 1
  Given I click "#btn-new" and type "abc" in input id=42
  When I POST /orders with body {"customerId":42}
  Then the table orders has 1 row
```
### Bien
```gherkin
Feature: Descuento por volumen
  Scenario: Pedido superior a 100 EUR recibe 10% de descuento
    Given un cliente estándar
    And un pedido con total de 150.00 EUR
    When se calcula el precio final
    Then el descuento aplicado es de 15.00 EUR
```
```java
@When("se calcula el precio final")
void priceIsCalculated() {
    result = pricing.finalPrice(order);   // step fino: delega en el dominio
}
```
Librería y versión (p. ej. Cucumber-JVM con JUnit Platform): TODO-VERIFY.

## Checklist de revisión
- [ ] Un lector de negocio entiende el escenario sin ver código.
- [ ] Sin detalles técnicos (selectores, URLs, SQL) en el `.feature`.
- [ ] Escenarios independientes entre sí.
- [ ] Steps sin lógica de negocio.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Ejecución de escenarios en la fase `verify` | 1 | pipeline del proyecto generado (pendiente) |
| Revisión de lenguaje de dominio en `.feature` | 4 | revisión humana (negocio + QA) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `tdd`, `e2e-testing`, `test-strategy`, `api-testing`.
- Fuentes: documentación oficial de Cucumber (https://cucumber.io/docs) — TODO-VERIFY versión y módulo JUnit Platform.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
