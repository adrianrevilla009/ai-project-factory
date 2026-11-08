---
name: java-memory-model
description: Usar al compartir estado mutable entre hilos sin locks - visibilidad, happens-before, volatile, publicación segura e inmutabilidad.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Java Memory Model

## Cuándo aplicar y cuándo no
- Aplica a campos mutables accedidos por más de un hilo, singletons, caches propias, flags de parada y lazy-init.
- No aplica a datos confinados a un hilo o ya protegidos por una estructura concurrente de `java.util.concurrent`.

## Reglas
- **MUST** que toda escritura compartida tenga una relación *happens-before* con la lectura: `synchronized`, `volatile`, `Lock`, `final`, estructuras concurrentes o `Thread.start/join`.
- **MUST** declarar `volatile` los flags de estado simples (parada, "ready") leídos por otros hilos.
- **MUST NOT** usar `volatile` para operaciones compuestas (`count++`, check-then-act); usar `AtomicInteger`/`LongAdder` o un lock.
- **MUST** publicar objetos de forma segura: campo `final`, `volatile`, dentro de un lock o vía `ConcurrentHashMap`/`BlockingQueue`.
- **MUST** preferir objetos inmutables (campos `final`, records, colecciones `List.copyOf`); son seguros sin sincronización.
- **MUST NOT** hacer double-checked locking sin `volatile`; preferir holder idiom o `enum`.
- **MUST NOT** dejar escapar `this` desde el constructor (registrar listeners, arrancar hilos).
- **SHOULD** tratar `long`/`double` no volátiles como no atómicos.
- **SHOULD** validar código sin locks con herramientas (jcstress), no con "funciona en mi máquina".

## Por qué
Sin happens-before, el compilador, la JIT y la CPU pueden reordenar o cachear: un hilo puede no ver nunca una escritura, o ver un objeto a medio construir. Los fallos son no deterministas, dependen de la arquitectura y escapan a los tests normales.

## Ejemplos
### Mal
```java
class Worker {
    private boolean running = true;           // no volatile: el bucle puede no terminar
    void stop() { running = false; }
    void run() { while (running) { process(); } }
}

class Config {
    private static Config instance;
    static Config get() {
        if (instance == null) { instance = new Config(); } // carrera, publicación insegura
        return instance;
    }
}
```
### Bien
```java
class Worker {
    private volatile boolean running = true;
    void stop() { running = false; }
    void run() { while (running) { process(); } }
}

class Config {
    private Config() {}
    private static class Holder { static final Config INSTANCE = new Config(); }
    static Config get() { return Holder.INSTANCE; }
}

private final LongAdder requests = new LongAdder();   // en vez de volatile long + ++
```

## Checklist de revisión
- [ ] Cada campo mutable compartido tiene una sincronización identificable.
- [ ] Sin `volatile` en operaciones compuestas.
- [ ] Sin DCL sin `volatile`; sin `this` escapando.
- [ ] Preferencia por inmutabilidad.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de estado compartido | 3 | agente `code-reviewer` |
| Análisis estático (SpotBugs/ErrorProne) | pendiente | TODO-VERIFY herramienta y versión |
| Pruebas de carrera con jcstress | pendiente | ver `concurrency-testing` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `locks-and-synchronization`, `concurrent-collections`, `concurrency-testing`.
- Fuentes: JLS capítulo 17 (docs.oracle.com/javase/specs) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
