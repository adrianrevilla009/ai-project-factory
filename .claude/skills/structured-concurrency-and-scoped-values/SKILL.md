---
name: structured-concurrency-and-scoped-values
description: Usar al lanzar subtareas concurrentes que deben vivir y morir juntas, o al sustituir ThreadLocal por ScopedValue; estado de los JEP.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Structured concurrency y Scoped Values

## Cuándo aplicar y cuándo no
- Aplica a fan-out de varias llamadas independientes cuyo resultado se combina, y a datos de contexto inmutables (usuario, trace id) compartidos con subtareas.
- No aplica si el proyecto no admite APIs en preview, o a tareas fire-and-forget de larga vida.

## Reglas
- **MUST** comprobar el estado del JEP en la versión de JDK del proyecto: `StructuredTaskScope` ha sido API en preview en varias versiones y su forma ha cambiado; `ScopedValue` pasó a definitivo más tarde.
- **MUST NOT** usar APIs en preview en código de producción sin decisión explícita (ADR) y `--enable-preview` documentado en el build.
- **MUST** si no hay preview: lograr el mismo efecto con `ExecutorService` + `close()` en try-with-resources, y cancelar hermanas ante fallo.
- **MUST** que el ámbito de la tarea cierre antes que el método que la abrió (try-with-resources); nada de subtareas que sobrevivan al llamante.
- **MUST** definir política de fallo: "todas o ninguna" (cancelar al primer error) o "la primera que acabe".
- **SHOULD** preferir `ScopedValue` a `ThreadLocal` para contexto inmutable; es heredado por subtareas del ámbito estructurado.
- **MUST NOT** mutar un `ScopedValue`; se rebindea con `ScopedValue.where(...).run(...)`.
- **SHOULD** poner timeout global del ámbito.

## Por qué
Con `Future` suelto, si una subtarea falla las otras siguen consumiendo recursos y se filtran hilos. El ciclo de vida acotado hace que el error, la cancelación y los thread dumps respeten la estructura del código. `ScopedValue` es inmutable y de vida acotada, sin las fugas de `ThreadLocal`.

## Ejemplos
### Mal
```java
Future<User> u = pool.submit(() -> users.find(id));
Future<List<Order>> o = pool.submit(() -> orders.byUser(id));
return new Profile(u.get(), o.get()); // si u falla, o sigue ejecutándose
```
### Bien (sin preview, patrón equivalente)
```java
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    var u = exec.submit(() -> users.find(id));
    var o = exec.submit(() -> orders.byUser(id));
    try {
        return new Profile(u.get(2, TimeUnit.SECONDS), o.get(2, TimeUnit.SECONDS));
    } catch (ExecutionException | TimeoutException e) {
        u.cancel(true); o.cancel(true);
        throw new ProfileUnavailableException(id, e);
    }
}
```
### Con ScopedValue (solo si el JDK del proyecto lo trae definitivo)
```java
static final ScopedValue<String> TRACE_ID = ScopedValue.newInstance();
ScopedValue.where(TRACE_ID, traceId).run(() -> handler.handle(req));
```

## Criterios de decisión y trampas
### Cómo decidir
- Usa concurrencia estructurada cuando varias subtareas forman una unidad que debe fallar o cancelarse junta; es más segura que lanzar tareas sueltas.
- Valores con ámbito para pasar contexto de solo lectura a las subtareas en lugar de variables locales de hilo.
### Trampas frecuentes
- Depender de una API en vista previa sin plan de salida.
- Lanzar subtareas que sobreviven a la operación que las inició.
- Usar valores con ámbito como almacén mutable.
- Ignorar la cancelación y las excepciones de las subtareas.
- Mezclar el modelo estructurado con ejecutores globales.
### Evidencia
- El código documenta qué ocurre con las subtareas cuando una falla y hay una prueba que lo cubre.

## Checklist de revisión
- [ ] Estado del JEP verificado para el JDK del proyecto.
- [ ] Sin preview no declarado.
- [ ] Subtareas no sobreviven al método; cancelación en fallo.
- [ ] Timeout definido.
- [ ] `ThreadLocal` sustituido o justificado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de uso de preview y ciclo de vida | 3 | agente `code-reviewer` |
| Flag `--enable-preview` en Maven | pendiente | policy de build (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `virtual-threads`, `completablefuture-patterns`, `async-and-context-propagation`.
- Fuentes: JEPs de Structured Concurrency y Scoped Values en openjdk.org/jeps.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
