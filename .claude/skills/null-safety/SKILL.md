---
name: null-safety
description: Usar al escribir o revisar APIs, parámetros, retornos y uso de Optional en Java para evitar NullPointerException y definir el contrato de nulos.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Seguridad frente a nulos

## Cuándo aplicar y cuándo no
- Aplica a firmas de métodos públicos, constructores, retornos de repositorios y servicios, y campos de DTOs.
- No aplica a código interno trivial de un solo método ni a campos mapeados por frameworks que exigen `null` (columnas JPA nullable).

## Reglas
- **MUST** tratar `null` como "no permitido" salvo que el contrato diga lo contrario; validar en el borde con `Objects.requireNonNull(x, "x")`.
- **MUST** devolver `Optional<T>` desde métodos de búsqueda que puedan no encontrar resultado.
- **MUST NOT** devolver `null` desde métodos que devuelven colecciones o arrays: devolver colección vacía.
- **MUST NOT** usar `Optional` como campo, parámetro de método ni elemento de colección.
- **MUST NOT** llamar `Optional.get()` sin comprobación; usar `orElseThrow(() -> new NotFoundException(...))`, `map`, `ifPresent` u `orElse`.
- **SHOULD** declarar la política de nulos del paquete con anotaciones (`@NullMarked` de JSpecify o equivalente de Spring).
- **SHOULD** usar `Objects.requireNonNullElse` / `Map.getOrDefault` antes que comprobaciones manuales repetidas.
- **MUST NOT** devolver `Boolean` nulo como tercer estado; usar un enum.

## Por qué
`NullPointerException` es la excepción más común y casi siempre aparece lejos del punto donde nació el nulo. Fallar rápido en el borde da un mensaje útil; `Optional` en retornos obliga al llamante a decidir. Como parámetro o campo, `Optional` añade ruido y puede ser él mismo `null`.

## Ejemplos
### Mal
```java
public List<Order> findOrders(String customerId) {
    if (customerId == null) return null;           // contrato oculto
    return repo.find(customerId);
}
public User load(Optional<String> id) {            // Optional como parámetro
    return repo.findById(id.get).get;          // dos get sin comprobar
}
```
### Bien
```java
public List<Order> findOrders(String customerId) {
    Objects.requireNonNull(customerId, "customerId");
    return repo.find(customerId);                  // vacía, nunca null
}
public User load(String id) {
    return repo.findById(id)                       // Optional<User>
        .orElseThrow(() -> new UserNotFoundException(id));
}
```

## Checklist de revisión
- [ ] Los parámetros obligatorios se validan en el borde.
- [ ] Ningún método devuelve `null` en lugar de vacío u `Optional`.
- [ ] No hay `Optional` en campos ni parámetros.
- [ ] No hay `.get()` sin `isPresent`/`orElseThrow`.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep `java-optional-get` (heurística amplia, sin ejecutar; no activar tal cual) | 1 | `policies/semgrep/java-language-pitfalls.yaml` |
| Revisión de contratos de nulos | 3 | agente `code-reviewer` (pendiente de definir) |

> Estado: la regla Semgrep solo marca `get()` sobre receptores tipados como `Optional` y está probada en `tests/semgrep/`.

## Relacionados, fuentes y mantenimiento
- Relacionados: `exceptions-and-error-handling`, `immutability-and-value-objects`, `generics-and-api-design`.
- Fuentes: Javadoc de `java.util.Optional` y `java.util.Objects` (oracle/openjdk); JSpecify (jspecify.dev); no verificado en línea.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
