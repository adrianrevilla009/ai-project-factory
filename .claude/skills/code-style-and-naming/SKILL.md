---
name: code-style-and-naming
description: Usar al nombrar, formatear y estructurar código Java (convenciones de nombres, tamaño de métodos, comentarios, imports y herramientas de formato automático).
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Estilo de código y nombres

## Cuándo aplicar y cuándo no
- Aplica a todo código Java de proyectos generados (main y test).
- No aplica a código generado (MapStruct, OpenAPI, protobuf), que se excluye del formateo y del análisis de estilo.

## Reglas
- **MUST** seguir las convenciones Java: `UpperCamelCase` clases/records, `lowerCamelCase` métodos y variables, `UPPER_SNAKE_CASE` constantes, paquetes en minúsculas sin guiones bajos.
- **MUST** que los identificadores y ficheros estén en inglés; los comentarios y documentación humana en español.
- **MUST** nombrar por intención del dominio (`overdueInvoices`), no por tipo (`list2`) ni abreviaturas crípticas (`cstmrLst`).
- **MUST** usar verbos para métodos y sustantivos para tipos; booleanos como pregunta (`isActive`, `hasPendingItems`).
- **MUST NOT** usar prefijos/sufijos vacíos (`IOrderService`, `OrderServiceImpl` cuando hay una sola implementación); nombrar la implementación por lo que la distingue (`JpaOrderRepository`).
- **SHOULD** métodos de ≤ ~30 líneas y una sola responsabilidad; clases cohesivas; complejidad ciclomática baja.
- **MUST NOT** dejar código comentado, `TODO` sin responsable/ticket, ni imports con comodín (`import x.*`).
- **SHOULD** comentar el *porqué*, no el *qué*; si hace falta explicar qué hace, renombrar o extraer.
- **MUST** delegar el formato (indentación, espacios, orden de imports) a una herramienta automática ejecutada en el build; **MUST NOT** discutir formato en revisión.
- **SHOULD** un tipo público de primer nivel por fichero; tests nombrados por comportamiento (`rejectsExpiredToken`).

## Por qué
El código se lee mucho más de lo que se escribe; los nombres de dominio reducen la carga mental. El formato automático elimina ruido en los diffs y discusiones sin valor. Las interfaces `I...`/`...Impl` añaden indirección sin información.

## Ejemplos
### Mal
```java
import java.util.*;
public class OrderServiceImpl implements IOrderService {
    // get list
    public List getL(int s) {
        List l = new ArrayList();
        // for (Order o : all) { ... }
        return l;
    }
}
```
### Bien
```java
public class InvoiceService {
    private final InvoiceRepository invoices;
    private final Clock clock;

    InvoiceService(InvoiceRepository invoices, Clock clock) {
        this.invoices = invoices;
        this.clock = clock;
    }

    /** Vencidas hoy; se excluyen las ya reclamadas para no duplicar avisos. */
    public List<Invoice> findOverdue() {
        return invoices.findDueBefore(LocalDate.now(clock)).stream()
            .filter(invoice -> !invoice.reminderSent())
            .toList();
    }
}
```

## Checklist de revisión
- [ ] Nombres de dominio en inglés y convención Java.
- [ ] Sin `I...`/`...Impl` innecesarios, sin imports `*`, sin código comentado.
- [ ] Métodos cortos y cohesivos.
- [ ] El formateador y el linter pasan en el build.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Formateador (p. ej. Spotless) y Checkstyle en Maven, verificados en CI (el proyecto generado debe configurarlos; herramienta y versión) | 1 | `pom.xml` del proyecto generado (pendiente) |
| Revisión de nombres y cohesión | 3 | agente `code-reviewer` (pendiente de definir) |

> Estado: la fábrica solo define la regla; la configuración concreta pertenece al proyecto generado (ADR-0038).

## Relacionados, fuentes y mantenimiento
- Relacionados: `modern-java-idioms`, `generics-and-api-design`, `code-smells-and-refactoring`, `solid`, `no-lombok`.
- Fuentes: Oracle "Code Conventions for the Java Programming Language" y Google Java Style Guide; no consultado en línea.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
