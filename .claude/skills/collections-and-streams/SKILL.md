---
name: collections-and-streams
description: Usar al elegir colecciones, devolver listas o escribir pipelines de Streams en Java; cubre inmutabilidad, complejidad, efectos laterales y legibilidad.
metadata:
  block: "01-java-language"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Colecciones y Streams

## Cuándo aplicar y cuándo no
- Aplica a cualquier código que manipule `List`, `Set`, `Map` o `Stream`.
- No aplica a consultas de base de datos (agregar en SQL, ver `projections-and-dtos`) ni a procesamiento reactivo (`reactive-vs-blocking`).

## Reglas
- **MUST** declarar variables, parámetros y retornos con la interfaz (`List`, `Map`), no la implementación.
- **MUST** devolver colecciones inmutables (`List.copyOf`, `Stream.toList()`, `Collections.unmodifiableList` solo como vista) desde APIs públicas.
- **MUST NOT** modificar una colección mientras se itera (`ConcurrentModificationException`); usar `removeIf` o construir una nueva.
- **MUST NOT** producir efectos laterales en `map`/`filter`/`peek`; `forEach` solo como operación terminal final.
- **MUST NOT** reutilizar un `Stream` ya consumido.
- **MUST NOT** usar `parallelStream()` en servicios web sin medir: comparte el `ForkJoinPool` común y bloquea otras peticiones.
- **SHOULD** usar un bucle `for` cuando el pipeline necesita más de ~4 pasos, estado mutable o manejo de excepciones checked.
- **SHOULD** dimensionar `HashMap`/`ArrayList` cuando el tamaño es conocido y grande.
- **MUST** usar `EnumMap`/`EnumSet` para claves enum, y `Collectors.toMap` con función de fusión si las claves pueden repetirse (si no, lanza `IllegalStateException`).
- **MUST NOT** usar `LinkedList` por defecto; `ArrayList` o `ArrayDeque`.

## Por qué
Devolver la colección interna permite que el llamante rompa invariantes. Los streams con efectos laterales son difíciles de razonar y fallan al paralelizar. `parallelStream` sobre I/O o en un servidor concurrente degrada la latencia de todos.

## Ejemplos
### Mal
```java
public ArrayList<Item> items() { return items; }            // implementación + mutable

List<String> names = new ArrayList<>();
users.stream().filter(User::active)
     .forEach(u -> names.add(u.name()));                    // efecto lateral
Map<String, User> byEmail =
    users.stream().collect(Collectors.toMap(User::email, u -> u)); // explota si hay duplicados
```
### Bien
```java
public List<Item> items() { return List.copyOf(items); }

List<String> names = users.stream()
    .filter(User::active)
    .map(User::name)
    .toList();

Map<String, User> byEmail = users.stream()
    .collect(Collectors.toMap(User::email, u -> u, (a, b) -> a));
```

## Criterios de decisión y trampas
### Cómo decidir
- Un bucle cuando hay efectos laterales o estado; un stream cuando transformas y filtras sin efectos.
- Elige la colección por su coste de acceso y su semántica (orden, unicidad), no por costumbre.
- Devuelve vistas inmutables o copias, no tus estructuras internas.
### Trampas frecuentes
- Streams paralelos sin medir: suelen empeorar el rendimiento con pocas tareas o tareas pequeñas.
- Efectos laterales dentro de `map` o `filter`.
- Modificar una colección mientras se recorre.
- Un stream que se consume dos veces.
- Pipelines de diez etapas que nadie puede depurar.
### Evidencia
- Las operaciones sobre colecciones grandes tienen una medición que justifica la elección.

## Checklist de revisión
- [ ] Las APIs devuelven interfaces e inmutables.
- [ ] Los streams no mutan estado externo.
- [ ] No hay `parallelStream` sin medición.
- [ ] `toMap` tiene función de fusión cuando procede.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de código | 3 | agente `code-reviewer` (pendiente de definir) |
| Regla Semgrep contra `parallelStream()` en servicios | 1 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `immutability-and-value-objects`, `concurrent-collections`, `modern-java-idioms`, `projections-and-dtos`.
- Fuentes: Javadoc de `java.util.stream` y `java.util.Collections`; no consultado en línea.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
