---
name: architecture-testing-archunit
description: "Usar al convertir reglas de arquitectura (capas, dependencias, ciclos, nombres) en tests ArchUnit ejecutados en cada build."
metadata:
  block: "08-testing-quality"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Tests de arquitectura con ArchUnit

## Cuándo aplicar y cuándo no
- Aplica a toda regla estructural comprobable sobre el bytecode: dependencias entre paquetes, ciclos, anotaciones, convenciones.
- No aplica a decisiones de diseño no formalizables (calidad de un modelo de dominio): revisión humana. Las reglas concretas de capas están en `layering-rules-archunit`.

## Reglas
- **MUST** codificar como test ArchUnit cada regla arquitectónica que pueda romperse con un `import`.
- **MUST** ejecutarlos con Surefire en cada build (son tests unitarios rápidos).
- **MUST** importar solo las clases de producción (`ImportOption.DoNotIncludeTests`).
- **MUST** que cada regla tenga mensaje con `.because("...")` que explique el porqué y enlace al ADR/skill.
- **SHOULD** reutilizar las reglas de `policies/archunit/` copiándolas al módulo de test del proyecto.
- **SHOULD** añadir reglas de ciclos (`slices().matching(...).should().beFreeOfCycles()`).
- **SHOULD** tratar la deuda existente con `FreezingArchRule` y un plan de reducción, no con exclusiones silenciosas.
- **MUST NOT** relajar o borrar una regla para que pase el build sin ADR que lo justifique.
- **MUST NOT** usar `@SuppressWarnings`-style excepciones amplias (`resideInAnyPackage("..")`) que vacían la regla.

## Por qué
Una arquitectura que solo está en un diagrama se erosiona. Un test que falla en el PR es el único mecanismo que escala sin depender de que alguien lo recuerde en la revisión.

## Ejemplos
### Mal
```text
Wiki: "el dominio no debe depender de Spring ni de la infraestructura".
(nadie lo comprueba; tres meses después el dominio importa @Autowired)
```
### Bien
```java
@AnalyzeClasses(packages = "com.acme.orders", importOptions = ImportOption.DoNotIncludeTests.class)
class ArchitectureTest {

    @ArchTest
    static final ArchRule domain_is_framework_free =
        noClasses().that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage("org.springframework..", "jakarta.persistence..")
            .because("el dominio es independiente del framework (ver hexagonal)");

    @ArchTest
    static final ArchRule no_cycles_between_modules =
        slices().matching("com.acme.orders.(*)..").should().beFreeOfCycles();
}
```
Reglas reales reutilizables: `policies/archunit/DomainIsolationRules.java`, `HexagonalArchitectureRules.java`, `ModuleBoundaryRules.java`. Versión de ArchUnit.

## Criterios de decisión y trampas
### Cómo decidir
- Una regla ArchUnit para todo lo que se rompe con un `import`; lo que no se puede comprobar estáticamente va a revisión o a un ADR.
- En un monolito modular, reglas por módulo (slices) además de por capa.
### Trampas frecuentes
- Reglas tan generales que nunca fallan, sin un caso que demuestre que fallarían.
- Reglas que pasan porque no encuentran clases (conjunto vacío).
- Congelar violaciones sin un plan para reducirlas.
- Importar también las clases de test.
- Mensajes sin `because` que no explican el porqué.
### Evidencia
- Cada regla tiene un ejemplo que debe fallar y enlaza al ADR o a la skill que la justifica.

## Checklist de revisión
- [ ] Cada regla de arquitectura documentada tiene su test.
- [ ] Los tests ignoran clases de test y llevan `.because(...)`.
- [ ] Sin exclusiones amplias; deuda congelada con plan.
- [ ] Cambios en reglas referencian ADR.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Reglas ArchUnit de ejemplo | 1 | `policies/archunit/DomainIsolationRules.java`, `HexagonalArchitectureRules.java`, `ModuleBoundaryRules.java` |
| Ejecución en `mvn test` | 1 | módulo de test del proyecto generado |
| Revisión de cambios a reglas | 4 | revisión humana + ADR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `layering-rules-archunit`, `hexagonal`, `clean-architecture`, `modular-monolith`, `evolutionary-architecture-fitness-functions`.
- Fuentes: guía de usuario de ArchUnit (https://www.archunit.org/userguide/html/000_Index.html).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
