---
name: locks-and-synchronization
description: Usar al proteger estado compartido con synchronized, ReentrantLock, ReadWriteLock o atómicos; orden de locks, deadlocks y alcance.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Locks y sincronización

## Cuándo aplicar y cuándo no
- Aplica a secciones críticas en memoria de una sola JVM.
- No aplica a exclusión entre instancias/pods (ver `distributed-locking`) ni a concurrencia sobre filas de BD (ver `optimistic-locking`, `pessimistic-locking`).

## Reglas
- **MUST** mantener la sección crítica mínima y sin I/O, llamadas remotas ni código ajeno (callbacks) dentro.
- **MUST** liberar `Lock` en `finally`; usar `tryLock(timeout)` cuando haya riesgo de espera larga.
- **MUST** fijar un orden global al adquirir varios locks (p. ej. por id ascendente) para evitar deadlocks.
- **MUST NOT** sincronizar sobre `this`, `String`, enteros "boxed" ni objetos públicos; usar un `private final Object lock`.
- **MUST NOT** llamar a métodos *alien* (sobrescribibles, listeners) con un lock tomado.
- **SHOULD** preferir `AtomicReference`/`LongAdder`/`ConcurrentHashMap.compute` antes que un lock manual.
- **SHOULD** usar `ReentrantLock` en vez de `synchronized` si se bloquea con I/O bajo virtual threads en Java < 24 (ver `virtual-threads`).
- **SHOULD** usar `StampedLock`/`ReadWriteLock` solo con evidencia de lecturas dominantes; son más difíciles de usar bien.
- **MUST** documentar con `@GuardedBy` (o comentario) qué lock protege cada campo.

## Por qué
La mayoría de errores no son falta de lock, sino lock mal acotado: sección demasiado larga (contención), orden inconsistente (deadlock) o lock sobre un objeto que otros también usan. Un deadlock en producción solo se ve con thread dump.

## Ejemplos
### Mal
```java
void transfer(Account a, Account b, long amt) {
    synchronized (a) {
        synchronized (b) {      // transfer(a,b) y transfer(b,a) en paralelo: deadlock
            a.debit(amt); b.credit(amt);
        }
    }
}
```
### Bien
```java
void transfer(Account a, Account b, long amt) {
    Account first = a.id() < b.id() ? a : b;
    Account second = first == a ? b : a;
    first.lock().lock();
    try {
        second.lock().lock();
        try { a.debit(amt); b.credit(amt); }
        finally { second.lock().unlock(); }
    } finally { first.lock().unlock(); }
}
```
```java
// sin lock manual
counters.merge(key, 1L, Long::sum);
```

## Checklist de revisión
- [ ] Cada campo compartido indica qué lo protege.
- [ ] `unlock` en `finally`; `tryLock` si procede.
- [ ] Orden de adquisición coherente.
- [ ] Sin I/O ni código ajeno dentro del lock.
- [ ] Sin `synchronized(this)` ni sobre objetos compartidos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Regla Semgrep contra `synchronized (this)` y `Thread.sleep` en secciones críticas | pendiente | `policies/semgrep/` (pendiente) |
| Revisión de orden de locks | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `java-memory-model`, `concurrent-collections`, `distributed-locking`, `concurrency-testing`.
- Fuentes: Javadoc de `java.util.concurrent.locks`.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
