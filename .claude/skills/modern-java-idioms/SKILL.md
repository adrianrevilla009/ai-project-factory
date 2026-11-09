---
name: modern-java-idioms
description: Usar al escribir o revisar Java nuevo para elegir records, sealed types, pattern matching, switch expressions, text blocks y var de forma idiomática.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Modernos idiomas de Java

## Cuándo aplicar y cuándo no
- Aplica a todo código Java nuevo o modificado de proyectos generados (Java LTS vigente,, ver ADR-0001).
- No aplica a código generado (MapStruct, OpenAPI, protobuf) ni a APIs públicas que deban conservar compatibilidad con una versión de Java anterior.

## Reglas
- **MUST** usar `record` para portadores de datos inmutables (DTO, eventos, value objects simples) en lugar de clases con getters manuales o Lombok (D27).
- **MUST** usar `switch` como expresión con `->`, sin `break` ni fall-through accidental.
- **SHOULD** modelar variantes cerradas con `sealed interface` + records y `switch` con pattern matching sin `default`, para que el compilador exija exhaustividad.
- **SHOULD** usar `instanceof` con patrón (`if (o instanceof Foo f)`) en vez de cast manual.
- **SHOULD** usar text blocks (`"""`) para JSON/SQL/GraphQL embebido en tests o consultas fijas.
- **SHOULD** usar `var` solo cuando el tipo es evidente en la misma línea (`var users = new ArrayList<User>()`).
- **MUST NOT** usar `var` para tipos devueltos por métodos cuyo nombre no revela el tipo, ni en lambdas con parámetros ambiguos.
- **MUST NOT** añadir un `default` a un `switch` sobre un `sealed` solo para silenciar al compilador: oculta variantes nuevas.
- **SHOULD** preferir `Stream.toList()` (inmutable) a `collect(Collectors.toList())`.

## Por qué
Las construcciones modernas mueven errores de tiempo de ejecución a tiempo de compilación: un `sealed` + `switch` exhaustivo falla al compilar cuando se añade una variante, mientras que `if/else` con `instanceof` falla en producción. Los records eliminan boilerplate sin necesidad de Lombok. Disponibilidad por versión: verificar en las JEP/notas de versión del JDK elegido.

## Ejemplos
### Mal
```java
public String describe(Object shape) {
    if (shape instanceof Circle) {
        Circle c = (Circle) shape;
        return "circle " + c.radius();
    } else if (shape instanceof Square) {
        return "square";
    }
    return "unknown";
}
```
### Bien
```java
sealed interface Shape permits Circle, Square {}
record Circle(double radius) implements Shape {}
record Square(double side) implements Shape {}

static String describe(Shape shape) {
    return switch (shape) {
        case Circle c -> "circle " + c.radius();
        case Square s -> "square " + s.side();
    };
}
```

## Checklist de revisión
- [ ] Los portadores de datos son `record`, no clases con getters/setters.
- [ ] Los `switch` sobre tipos cerrados son exhaustivos y sin `default` espurio.
- [ ] No hay casts tras `instanceof` ni `break` en switches nuevos.
- [ ] `var` solo donde el tipo es obvio.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de estilo y diseño de tipos | 3 | agente `code-reviewer` (pendiente de definir) |
| Compilación con `-Xlint:all -Werror` (el proyecto generado debe activarlo) | 1 | `pom.xml` del proyecto generado (pendiente) |

> Estado: sin artefacto automático específico en la fábrica; el lint del compilador lo aporta el proyecto generado.

## Relacionados, fuentes y mantenimiento
- Relacionados: `immutability-and-value-objects`, `no-lombok`, `code-style-and-naming`, `null-safety`.
- Fuentes: JEP 395 (records), JEP 409 (sealed), JEP 441 (pattern matching for switch) en openjdk.org.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
