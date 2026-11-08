---
name: pessimistic-locking
description: Usar al necesitar bloqueo de filas (SELECT FOR UPDATE, SKIP LOCKED) por alta contención, colas en BD o deadlocks.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Bloqueo pesimista

## Cuándo aplicar y cuándo no
- Aplica cuando la contención es alta y el coste de reintentar es mayor que el de esperar, o al reclamar trabajo de una tabla-cola.
- No aplica como defecto: el bloqueo optimista es la primera opción (`optimistic-locking`).

## Reglas
- **MUST** justificar por escrito por qué no basta bloqueo optimista o un `UPDATE` atómico.
- **MUST** definir siempre timeout de bloqueo (`jakarta.persistence.lock.timeout`, o `NOWAIT`/`lock_timeout` del motor) — comprobar soporte por dialecto; nunca esperar indefinidamente.
- **MUST** mantener la transacción mínima: tomar el bloqueo tarde y soltarlo pronto (commit); sin I/O externo mientras se retiene.
- **MUST** adquirir bloqueos sobre varias filas/tablas siempre en el mismo orden (por id ascendente) para evitar deadlocks.
- **SHOULD** usar `FOR UPDATE SKIP LOCKED` para que varios workers reclamen filas de una tabla-cola sin pisarse.
- **MUST** manejar `PessimisticLockException`/`CannotAcquireLockException` y deadlocks con reintento acotado.
- **MUST NOT** usar `PESSIMISTIC_WRITE` en consultas con joins amplios; bloquea más filas de las previstas.
- **MUST NOT** sustituir con bloqueo de BD un lock distribuido entre servicios (ver `distributed-locking`).

## Por qué
El bloqueo pesimista serializa el acceso y retiene conexiones; mal usado provoca latencias en cola, agotamiento del pool y deadlocks. Con timeout y orden consistente es una herramienta correcta para colas y contención alta.

## Ejemplos
### Mal
```java
@Transactional
public void transfer(Long from, Long to, BigDecimal amount) {
    Account a = accounts.findByIdForUpdate(from);   // sin orden fijo
    Account b = accounts.findByIdForUpdate(to);     // transferencias cruzadas = deadlock
    a.debit(amount); b.credit(amount);
}
```
### Bien
```java
interface AccountRepository extends JpaRepository<Account, Long> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @QueryHints(@QueryHint(name = "jakarta.persistence.lock.timeout", value = "3000"))
    @Query("select a from Account a where a.id in :ids order by a.id")
    List<Account> lockAllOrdered(Collection<Long> ids);
}

@Transactional
public void transfer(Long from, Long to, BigDecimal amount) {
    Map<Long, Account> locked = accounts.lockAllOrdered(List.of(from, to)).stream()
        .collect(Collectors.toMap(Account::getId, Function.identity()));
    locked.get(from).debit(amount);
    locked.get(to).credit(amount);
}
```
Claim de cola (SQL nativo, PostgreSQL):
```sql
SELECT id FROM jobs WHERE status = 'PENDING' ORDER BY id LIMIT 10 FOR UPDATE SKIP LOCKED;
```

## Checklist de revisión
- [ ] Justificado frente a bloqueo optimista.
- [ ] Timeout de bloqueo configurado.
- [ ] Orden de adquisición consistente.
- [ ] Transacción corta, sin I/O externo.
- [ ] Reintento ante deadlock/timeout.
- [ ] Test de concurrencia con dos hilos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de concurrencia con Testcontainers | 2 | pendiente (`db-testing`, `concurrency-testing`) |
| Regla Semgrep: `PESSIMISTIC_*` sin hint de timeout | 1 | pendiente (`policies/semgrep/`) |
| Revisión humana de cada uso | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `optimistic-locking`, `isolation-levels-and-anomalies`, `distributed-locking`, `connection-pooling`.
- Fuentes: Jakarta Persistence (`LockModeType`) y documentación del motor (`SELECT ... FOR UPDATE`, `SKIP LOCKED`) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
