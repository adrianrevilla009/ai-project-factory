---
name: rules-engines
description: "Usar al decidir si reglas de negocio cambiantes (precios, elegibilidad, scoring) van en código, tablas de decisión o un motor de reglas (Drools/DMN)."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Motores de reglas

## Cuándo aplicar y cuándo no
- Aplica cuando las reglas cambian con más frecuencia que el despliegue, las edita negocio o son numerosas y combinatorias.
- No aplica a unas pocas condiciones estables: un `switch` o una estrategia en Java es más simple y testeable.

## Reglas
- **MUST** empezar por código (patrón Strategy / specification) y justificar por escrito el salto a un motor.
- **MUST** comprobar licencia del motor elegido (D16). Drools/KIE y DMN de Camunda/Flowable: licencia y versión TODO-VERIFY en documentación oficial.
- **MUST** aislar el motor tras un puerto `PricingRulesPort`; entrada y salida son DTOs inmutables.
- **MUST** versionar reglas junto al código y probarlas con casos tabulares (given/expected).
- **MUST** registrar qué versión de reglas decidió cada resultado (trazabilidad, ver `audit-trail-and-activity-log`).
- **MUST NOT** permitir que reglas editadas en caliente lleguen a producción sin revisión y pruebas.
- **MUST NOT** dar acceso a servicios/BD al motor desde las reglas (efectos laterales).
- **SHOULD** preferir tablas de decisión (DMN) cuando negocio las mantiene.

## Por qué
Los motores prometen "cambiar reglas sin desplegar" pero trasladan el riesgo: reglas sin tests ni revisión rompen producción sin pasar por CI. Una decisión sin versión de reglas registrada es inauditable.

## Ejemplos
### Mal
```java
if (c.getType().equals("GOLD") && o.getTotal() > 100 && !o.isPromo() /* 40 condiciones más */) { ... }
```
### Bien
```java
public interface PricingRulesPort {
    PricingDecision evaluate(PricingInput input);
}
public record PricingDecision(BigDecimal discount, String rulesVersion) {}
```
```java
@ParameterizedTest
@CsvSource({"GOLD,150.00,0.10", "STANDARD,150.00,0.00"})
void discountByTier(String tier, BigDecimal total, BigDecimal expected) {
    var d = rules.evaluate(new PricingInput(tier, total));
    assertThat(d.discount()).isEqualByComparingTo(expected);
}
```

## Checklist de revisión
- [ ] Justificación de usar motor frente a código.
- [ ] Licencia verificada.
- [ ] Puerto + DTOs; reglas sin efectos laterales.
- [ ] Tests tabulares en CI; versión de reglas registrada.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Tests tabulares en CI del proyecto generado | 1 | tests del proyecto |
| Regla ArchUnit de aislamiento del motor | 1 | pendiente (`policies/archunit/`) |
| Revisión de la decisión de adoptar motor | 3 | revisión humana (ADR) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `workflow-bpm`, `audit-trail-and-activity-log`, `testing-slices`.
- Fuentes: documentación oficial de Drools/DMN: TODO-VERIFY (no consultada).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
