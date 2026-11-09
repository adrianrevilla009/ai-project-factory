---
name: concurrent-collections
description: Usar al elegir colecciones compartidas entre hilos (ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue) y al hacer operaciones atómicas sobre ellas.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Colecciones concurrentes

## Cuándo aplicar y cuándo no
- Aplica a mapas, listas y colas accedidos desde varios hilos (caches en memoria, contadores, colas de trabajo).
- No aplica a colecciones locales a un método ni a estado que debe vivir en BD/Redis compartido entre pods.

## Reglas
- **MUST NOT** compartir `HashMap`, `ArrayList` o `HashSet` entre hilos con escritores.
- **MUST** preferir `ConcurrentHashMap` a `Collections.synchronizedMap` salvo que se necesite bloqueo externo.
- **MUST** usar operaciones atómicas (`computeIfAbsent`, `merge`, `compute`, `putIfAbsent`); **MUST NOT** hacer `if (!map.containsKey(k)) map.put(k, v)`.
- **MUST** que la función pasada a `compute*` sea corta, sin I/O y sin tocar el mismo mapa (puede bloquear o lanzar excepción).
- **SHOULD** usar `CopyOnWriteArrayList` solo con lecturas dominantes y escrituras raras; cada escritura copia el array.
- **MUST** usar colas acotadas (`ArrayBlockingQueue`, `LinkedBlockingQueue(capacity)`) para productor/consumidor; nunca sin cota.
- **MUST NOT** asumir que `size()` o una iteración son instantáneas consistentes; son débilmente consistentes.
- **SHOULD** usar `LongAdder` para contadores con mucha contención.
- **MUST** definir expulsión/tamaño máximo en caches en memoria; preferir Caffeine a un mapa propio.

## Por qué
`HashMap` mal usado puede perder datos o, según la versión, bloquear el hilo. El patrón check-then-act sobre un mapa concurrente sigue siendo una carrera aunque cada llamada sea segura. Una cola sin cota esconde el problema hasta el OOM.

## Ejemplos
### Mal
```java
private final Map<String, Session> sessions = new HashMap<>();
Session get(String id) {
    if (!sessions.containsKey(id)) {        // carrera: dos hilos crean dos sesiones
        sessions.put(id, create(id));
    }
    return sessions.get(id);
}
```
### Bien
```java
private final ConcurrentMap<String, Session> sessions = new ConcurrentHashMap<>();
Session get(String id) {
    return sessions.computeIfAbsent(id, this::create); // create: rápido, sin I/O
}

private final BlockingQueue<Job> queue = new ArrayBlockingQueue<>(1_000);
boolean submit(Job j) { return queue.offer(j); }       // false = rechazar, no bloquear
```

## Checklist de revisión
- [ ] Ninguna colección no concurrente compartida con escrituras.
- [ ] Sin check-then-act; operaciones atómicas.
- [ ] Colas acotadas con política de rechazo.
- [ ] Funciones de `compute*` cortas y sin I/O.
- [ ] Caches con tamaño máximo.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep: `containsKey` seguido de `put` | 1 | `policies/semgrep/java-check-then-act-map.yaml` (probada con `semgrep --test`, ver `tests/semgrep/`) |
| Revisión de acotación de colas | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `java-memory-model`, `locks-and-synchronization`, `backpressure-and-bulkheads`, `caching`.
- Fuentes: Javadoc de `java.util.concurrent`.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
