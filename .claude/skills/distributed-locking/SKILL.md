---
name: distributed-locking
description: Usar al necesitar exclusión mutua entre varias instancias/pods (jobs únicos, recursos compartidos); locks con TTL, fencing tokens y alternativas.
metadata:
  block: "02-concurrency"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Locks distribuidos

## Cuándo aplicar y cuándo no
- Aplica cuando varias instancias pueden ejecutar a la vez la misma operación y solo una debe hacerlo (job programado, migración, reconciliación).
- No aplica si basta una restricción única en BD, un `UPDATE ... WHERE` condicional, locking optimista o una cola con consumidor único: son más simples y más seguros.

## Reglas
- **MUST** agotar primero alternativas sin lock: `UNIQUE`, versión optimista (`optimistic-locking`), `SELECT ... FOR UPDATE SKIP LOCKED`, cola particionada.
- **MUST** que todo lock tenga TTL/lease; un lock sin expiración deja el sistema bloqueado si el titular muere.
- **MUST** asumir que el titular puede perder el lock sin saberlo (pausa GC, partición): proteger el recurso con un *fencing token* monotónico que el recurso verifique, o hacer la operación idempotente.
- **MUST NOT** usar un lock distribuido como única garantía de corrección de dinero o inventario.
- **MUST** liberar solo si se es titular (valor único por adquisición, comparar-y-borrar atómico).
- **SHOULD** usar el almacén que el proyecto ya tiene y respeta D16 (sin licencias de pago): Postgres (`pg_advisory_xact_lock` o tabla con lease) o ShedLock (Apache-2.0, TODO-VERIFY) sobre JDBC para jobs.
- **MUST NOT** tomar un lock Redis de una sola instancia como si fuera consenso; Redlock es controvertido (TODO-VERIFY) y no sustituye al fencing.
- **SHOULD** acotar la sección crítica a bastante menos que el TTL y exponer métricas de adquisición/espera.
- En local se usa el mismo mecanismo sobre el Postgres de desarrollo; no se reproducen fallos de red/partición realistas de AWS.

## Por qué
Un lock distribuido es una pista de "probablemente solo yo", no una garantía: relojes, pausas y particiones permiten dos titulares. La corrección debe vivir en el recurso protegido (token, versión, idempotencia).

## Ejemplos
### Mal
```java
if (redis.setIfAbsent("job:close-day", "1")) {   // sin TTL, sin dueño
    closeDay();
    redis.delete("job:close-day");               // puede borrar el lock de otro
}
```
### Bien
```java
@Scheduled(cron = "0 0 2 * * *")
@SchedulerLock(name = "closeDay", lockAtMostFor = "PT30M", lockAtLeastFor = "PT1M")
public void closeDay() { service.closeDay(LocalDate.now().minusDays(1)); } // idempotente por fecha
```
```sql
-- fencing en el recurso: rechazar escrituras con token antiguo
UPDATE ledger SET balance = :b, last_token = :token
 WHERE id = :id AND last_token < :token;
```

## Checklist de revisión
- [ ] Se descartó restricción única/optimista/cola.
- [ ] Lock con TTL y dueño verificable.
- [ ] Operación protegida es idempotente o usa fencing token.
- [ ] No es la única barrera de integridad.
- [ ] Métricas de contención.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Revisión de diseño de exclusión mutua | 3 | agente `code-reviewer` / revisión humana |
| Regla de `@Scheduled` sin lock (ver `scheduling-and-batch`) | pendiente | `policies/semgrep/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `idempotency-and-deduplication`, `scheduling-and-batch`, `optimistic-locking`, `pessimistic-locking`.
- Fuentes: documentación de ShedLock y de Postgres (advisory locks); crítica de Kleppmann a Redlock (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
