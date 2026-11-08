---
name: mutation-testing
description: "Usar al medir la calidad real de los tests unitarios con PIT (pitest) en módulos Java de lógica de dominio y definir umbrales."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Mutation testing con PIT

## Cuándo aplicar y cuándo no
- Aplica a lógica de dominio y cálculo (reglas de negocio, dinero, validaciones) con tests unitarios rápidos.
- No aplica a código de infraestructura, controladores finos, DTOs ni a suites lentas de integración: el coste es multiplicativo.

## Reglas
- **MUST** usar PIT (`pitest-maven`) solo sobre paquetes de dominio, acotados con `targetClasses` y `targetTests`.
- **MUST** ejecutar PIT en CI nocturno o en PR sobre las clases modificadas (modo incremental), no en cada commit local.
- **MUST** fijar `mutationThreshold` para el módulo (inicio sugerido: 70) y subirlo gradualmente; no bajarlo para que pase el build.
- **MUST** tratar cada mutante superviviente como una de dos cosas: test que falta o código muerto/equivalente (documentarlo).
- **MUST NOT** perseguir 100 %: los mutantes equivalentes existen.
- **MUST NOT** usar la cobertura de líneas como sustituto: un test sin aserciones da cobertura y cero mutantes muertos.
- **SHOULD** excluir con `excludedClasses` generados (MapStruct), `toString` y logging.
- **SHOULD** usar `withHistory` / análisis incremental para reducir tiempos.

## Por qué
La cobertura dice qué código se ejecuta, no qué comportamiento se comprueba. PIT modifica el bytecode (invierte condiciones, cambia retornos) y comprueba que algún test falle; si no, la aserción no protege esa lógica.

## Ejemplos
### Mal
```java
@Test
void calculatesDiscount() {
    new DiscountCalculator().discountFor(customer, order); // sin aserción: 100 % líneas, 0 % mutantes muertos
}
```
### Bien
```java
@Test
void vipCustomerGetsTenPercentAtExactlyThreshold() {
    var discount = new DiscountCalculator().discountFor(vip(), orderOf("100.00"));
    assertThat(discount).isEqualByComparingTo("10.00"); // mata el mutante `>=` -> `>`
}
```
```xml
<plugin>
  <groupId>org.pitest</groupId>
  <artifactId>pitest-maven</artifactId>
  <!-- version: gestionada en el parent/BOM -->
  <configuration>
    <targetClasses><param>com.acme.orders.domain.*</param></targetClasses>
    <mutationThreshold>70</mutationThreshold>
  </configuration>
  <dependencies>
    <dependency><!-- JUnit 5 requiere el plugin pitest-junit5-plugin -->
      <groupId>org.pitest</groupId><artifactId>pitest-junit5-plugin</artifactId>
    </dependency>
  </dependencies>
</plugin>
```

## Checklist de revisión
- [ ] PIT limitado a paquetes de dominio.
- [ ] `mutationThreshold` definido y no reducido sin ADR.
- [ ] Supervivientes revisados: test añadido o equivalente documentado.
- [ ] Ejecución incremental o nocturna, no en cada build local.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| `mutationThreshold` en el pom del proyecto generado (falla el build) | 1 | `pom.xml` del proyecto generado (pendiente de plantilla; la fábrica no contiene plantillas, ADR-0038) |
| Job CI nocturno de PIT | 2 | pipeline del proyecto generado (pendiente) |
| Revisión de supervivientes | 3 | agente `test-automation` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `coverage-policy`, `unit-testing-java`, `property-based-testing`, `test-strategy`.
- Fuentes: https://pitest.org/quickstart/maven/ (comprobar parámetros y versión; no contrastado con la versión vigente a 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
