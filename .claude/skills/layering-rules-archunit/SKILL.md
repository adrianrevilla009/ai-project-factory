---
name: layering-rules-archunit
description: Usar al fijar o revisar reglas de capas, ciclos y dependencias permitidas con ArchUnit en un servicio Java.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Reglas de capas con ArchUnit

## Cuándo aplicar y cuándo no
- Aplica a cualquier servicio Java con una arquitectura declarada (capas, hexagonal, módulos) que deba mantenerse en el tiempo.
- No aplica a prototipos desechables. La estrategia general de testing de arquitectura vive en `architecture-testing-archunit` (bloque 08).

## Reglas
- **MUST** codificar la arquitectura elegida como tests ArchUnit que fallen el build (`mvn verify`).
- **MUST** incluir al menos: regla de capas, ausencia de ciclos entre paquetes/módulos y dominio sin dependencias de framework.
- **MUST** usar `@AnalyzeClasses(packages = ...)` acotado al paquete base, excluyendo tests si procede.
- **MUST NOT** relajar una regla para que pase el build: corregir el código o abrir una decisión (ADR) que cambie la regla.
- **SHOULD** usar `consideringOnlyDependenciesInLayers()` para no ahogar la regla en dependencias de librerías.
- **SHOULD** nombrar cada regla por la intención (`domain_does_not_depend_on_frameworks`).
- **SHOULD** usar `FreezingArchRule` solo para adoptar reglas en código heredado, con plan de descongelado.
- **MUST** fijar la versión de `archunit-junit5` en el BOM del proyecto.

## Por qué
Los diagramas y la documentación no impiden un `import` indebido; un test sí. Una regla ejecutable convierte la arquitectura en contrato y hace visible la erosión en el PR que la causa.

## Ejemplos
### Mal
```java
@ArchTest
static final ArchRule rule = classes().should().beAnnotatedWith(Service.class); // regla sin intención arquitectónica
// y en el PR: @ArchIgnore para que pase el build
```
### Bien
```java
@AnalyzeClasses(packages = "com.example.app")
class LayeringRules {
    @ArchTest
    static final ArchRule layers_respected =
        layeredArchitecture().consideringOnlyDependenciesInLayers()
            .layer("Web").definedBy("..web..")
            .layer("Application").definedBy("..application..")
            .layer("Domain").definedBy("..domain..")
            .whereLayer("Web").mayNotBeAccessedByAnyLayer()
            .whereLayer("Application").mayOnlyBeAccessedByLayers("Web")
            .whereLayer("Domain").mayOnlyBeAccessedByLayers("Application", "Web");

    @ArchTest
    static final ArchRule no_cycles =
        slices().matching("com.example.app.(*)..").should().beFreeOfCycles();
}
```

## Checklist de revisión
- [ ] Hay reglas de capas, ciclos y dominio puro.
- [ ] Los tests se ejecutan en `mvn verify` y en CI.
- [ ] Ninguna regla está ignorada o congelada sin motivo y fecha.
- [ ] Los nombres de regla expresan la intención.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Ejemplo de reglas ArchUnit (capas, dominio sin frameworks) | 1 | `policies/archunit/HexagonalArchitectureRules.java` |
| Ejemplo de reglas de módulos y ciclos | 1 | `policies/archunit/ModuleBoundaryRules.java` |
| Búsqueda de `@ArchIgnore`/`FreezingArchRule` sin justificar | 3 | revisión de PR (regla Semgrep pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `hexagonal`, `modular-monolith`, `architecture-testing-archunit`, `evolutionary-architecture-fitness-functions`.
- Fuentes: ArchUnit User Guide, https://www.archunit.org/userguide/html/000_Index.html.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
