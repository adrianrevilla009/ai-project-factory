---
name: no-lombok
description: Usar siempre que se pueda introducir Lombok o sus anotaciones; indica las alternativas con records y builders explícitos (D27, ADR-0027).
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Sin Lombok

## Cuándo aplicar y cuándo no
- Aplica a todo código y `pom.xml` de proyectos generados, y a dependencias transitivas que incluyan anotaciones Lombok.
- No aplica a la fábrica en sí (solo guías, ADR-0038) ni a documentación que cite Lombok para explicar la prohibición.

## Reglas
- **MUST NOT** añadir la dependencia `org.projectlombok:lombok` ni su procesador de anotaciones (ADR-0027).
- **MUST NOT** importar nada de `lombok.*` (`@Data`, `@Getter`, `@Builder`, `@Slf4j`, `@RequiredArgsConstructor`, `val`...).
- **MUST** usar `record` para datos inmutables (getters, `equals`, `hashCode`, `toString` generados por el lenguaje).
- **MUST** escribir builders explícitos cuando haya muchos parámetros opcionales (ver `generics-and-api-design`) o usar un record de opciones.
- **MUST** declarar el logger a mano: `private static final Logger log = LoggerFactory.getLogger(Foo.class);`.
- **MUST** escribir constructores explícitos para inyección de dependencias (un solo constructor, Spring lo inyecta sin anotación).
- **SHOULD** que el IDE genere getters/constructores cuando una clase mutable (entidad JPA) los necesite.
- **MUST NOT** introducir sustitutos que hagan lo mismo con generación de código opaca (p. ej. Immutables, AutoValue) sin ADR nuevo.

## Por qué
Decisión cerrada D27: código explícito, mejor soporte de herramientas (análisis estático, depuración, navegación) y menos magia en tiempo de compilación; Lombok depende de internals del compilador y puede romperse al actualizar el JDK. Los records cubren el caso más común.

## Ejemplos
### Mal
```java
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@Slf4j @Data @RequiredArgsConstructor
public class OrderService {
    private final OrderRepository repo;
}
```
### Bien
```java
public record OrderSummary(long id, String customerName) {}

public class OrderService {
    private static final Logger log = LoggerFactory.getLogger(OrderService.class);
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) {
        this.repo = Objects.requireNonNull(repo, "repo");
    }
}
```

## Checklist de revisión
- [ ] Ningún `import lombok.` ni dependencia Lombok en `pom.xml`.
- [ ] Datos inmutables como `record`; loggers y constructores explícitos.
- [ ] No se añadieron generadores alternativos sin ADR.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep contra `import lombok.` | 1 | `policies/semgrep/java-no-lombok.yaml` |
| Hook `forbidden-deps` sobre `pom.xml` (ADR-0027) | 2 | `.claude/hooks/post-tool-use/forbidden_deps.py` |
| Regla Enforcer `bannedDependencies` en el proyecto generado | 1 | `pom.xml` del proyecto generado (pendiente) |

> Estado: la regla Semgrep existe; el hook y la regla Enforcer están pendientes.

## Relacionados, fuentes y mantenimiento
- Relacionados: `modern-java-idioms`, `immutability-and-value-objects`, `logging-rules`, `dependency-injection-rules`.
- Fuentes: `catalog/adr/0027-lombok-prohibido.md`; Maven Enforcer Plugin (maven.apache.org).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
