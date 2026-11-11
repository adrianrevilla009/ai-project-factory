# archunit

Tres ejemplos de reglas de [ArchUnit](https://www.archunit.org), la librería de Java que convierte reglas de arquitectura en pruebas JUnit que se ejecutan en cada build.

**Estado: ejemplos sin ejecutar.** Se copian al módulo de pruebas del proyecto generado, sustituyendo el paquete base (`com.example`) por el del proyecto.

| Fichero | Qué impone | Skill de origen |
|---|---|---|
| `DomainIsolationRules.java` | El dominio no depende de frameworks ni de infraestructura | `ddd-tactical`, `hexagonal` |
| `HexagonalArchitectureRules.java` | Las capas de la arquitectura hexagonal solo dependen en la dirección permitida | `hexagonal`, `layering-rules-archunit` |
| `ModuleBoundaryRules.java` | En un monolito modular, solo la API pública de un módulo es accesible desde otro | `modular-monolith` |

## Buenas prácticas al adoptarlas
- Importar solo las clases de producción (`ImportOption.DoNotIncludeTests`).
- Que cada regla lleve `.because("...")` con el motivo y un enlace al ADR o a la skill.
- Probar cada regla con un caso que **demuestre que falla** cuando se viola.
- No «congelar» violaciones sin un plan para reducirlas.
