---
name: gof-patterns-in-practice
description: Usar al plantearse un patrón GoF (strategy, factory, decorator...) en Java/Spring y decidir si realmente aporta.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Patrones GoF en la práctica

## Cuándo aplicar y cuándo no
- Aplica cuando un problema de variación o de construcción encaja en un patrón y se duda entre patrón, lambda o código simple.
- No aplica para "meter" patrones en código que no los necesita. Primero el problema, después el patrón.

## Reglas
- **MUST** poder enunciar el problema concreto que resuelve el patrón (en el PR o comentario) antes de introducirlo.
- **SHOULD** usar Strategy con interfaces funcionales o `Map<Key, Handler>` en lugar de cadenas de `if/else` o `switch` que crecen.
- **SHOULD** usar Factory/builder para construcción compleja; para objetos de valor, `record` con validación en el constructor compacto.
- **SHOULD** usar Decorator (o AOP de Spring) para preocupaciones transversales; evitar herencia para ello.
- **MUST NOT** implementar Singleton manual; usar el ámbito de bean de Spring y evitar estado mutable compartido.
- **MUST NOT** usar Service Locator ni `ApplicationContext.getBean` en código de negocio.
- **SHOULD** preferir Observer vía eventos de Spring/dominio (`domain-events-in-spring`) a listeners manuales.
- **MUST NOT** nombrar clases por el patrón si no aportan semántica (`OrderFactoryImpl`, `StrategyManager`).

## Por qué
Los patrones son vocabulario compartido, no objetivos. En Java moderno muchos (Strategy, Command, Template Method) se reducen a lambdas o composición; Spring ya implementa Singleton, Proxy y Observer. Un patrón sin problema añade indirección sin beneficio.

## Ejemplos
### Mal
```java
String fee(String type, Money amount) {
    if (type.equals("CARD")) return amount.times(0.02);
    else if (type.equals("WIRE")) return amount.times(0.01);
    else if (type.equals("CASH")) return Money.ZERO;
    // crece con cada método de pago
}
```
### Bien
```java
interface FeeStrategy { PaymentType type(); Money fee(Money amount); }

@Component
class FeeCalculator {
    private final Map<PaymentType, FeeStrategy> byType;
    FeeCalculator(List<FeeStrategy> strategies) {
        this.byType = strategies.stream().collect(Collectors.toUnmodifiableMap(FeeStrategy::type, s -> s));
    }
    Money fee(PaymentType t, Money amount) {
        return Optional.ofNullable(byType.get(t)).orElseThrow(() -> new UnsupportedPayment(t)).fee(amount);
    }
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Usa un patrón por el problema que resuelve; muchas veces una función o un record lo resuelven con menos código.
- Nombra el patrón en el código solo si ayuda a quien lo lee.
### Trampas frecuentes
- Un patrón por obligación (fábrica de una sola clase).
- Singleton con estado global.
- Jerarquías de estrategias para dos casos.
- Patrones que esconden flujo de control sencillo.
- Documentar el patrón en vez de su motivo.
### Evidencia
- El patrón elegido se justifica con el cambio que absorbe.

## Checklist de revisión
- [ ] El patrón resuelve un problema presente y nombrado.
- [ ] No existe una alternativa más simple (lambda, `record`, método).
- [ ] No hay Singleton manual ni Service Locator.
- [ ] Los nombres expresan el dominio, no el patrón.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de PR; prohibición de `getBean` en código de negocio: regla Semgrep pendiente en `policies/semgrep/` | 3 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `solid`, `code-smells-and-refactoring`, `domain-events-in-spring`, `hexagonal`.
- Fuentes: Gamma, Helm, Johnson, Vlissides, "Design Patterns" (1994).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
