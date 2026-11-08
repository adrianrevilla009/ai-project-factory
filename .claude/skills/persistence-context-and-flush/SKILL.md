---
name: persistence-context-and-flush
description: "Usar al razonar sobre el contexto de persistencia: dirty checking, flush, detached/managed, clear y save() de Spring Data."
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Contexto de persistencia y flush

## Cuándo aplicar y cuándo no
- Aplica a código con `EntityManager`/repositorios dentro de transacciones, procesos que tocan muchas entidades y tests de persistencia.
- No aplica a acceso JDBC/jOOQ sin Hibernate.

## Reglas
- **MUST** entender que dentro de una transacción las entidades gestionadas se sincronizan solas (dirty checking) al hacer flush; no hace falta `save()` tras modificar una entidad gestionada.
- **MUST NOT** esperar que los cambios estén en BD antes del commit: el flush ocurre en commit, antes de ciertas consultas (modo AUTO) o con `flush()` explícito.
- **SHOULD** llamar a `flush()` solo cuando se necesite detectar una violación de constraint en un punto concreto o antes de una consulta nativa sobre datos recién cambiados.
- **MUST** liberar el contexto (`flush()` + `clear()`) cada lote en procesos con miles de entidades para evitar crecimiento de memoria y dirty checking lento (ver `batching-and-bulk-ops`).
- **MUST NOT** guardar `EntityManager` ni entidades gestionadas en campos de singletons ni compartirlos entre hilos.
- **MUST** recordar que `@Modifying` en JPQL/SQL no actualiza las entidades ya cargadas: usar `clearAutomatically = true` o recargar.
- **SHOULD** marcar `@Transactional(readOnly = true)` en lecturas: evita snapshots para dirty checking en Hibernate (comprobar detalle por versión).
- **MUST NOT** hacer `save()` en bucle sobre entidades ya gestionadas esperando un INSERT/UPDATE inmediato.
- **SHOULD** usar `getReferenceById` para asociar sin cargar la fila completa.

## Por qué
El contexto es una caché de primer nivel con identidad por id y seguimiento de cambios. Ignorarlo produce escrituras "mágicas" inesperadas, memoria que crece en lotes y lecturas obsoletas tras actualizaciones masivas.

## Ejemplos
### Mal
```java
@Transactional
public void archiveOld() {
    orders.findAll().forEach(o -> o.setStatus(Status.ARCHIVED)); // 1M entidades en memoria
    orders.markCancelledBulk();                                  // @Modifying: las cargadas siguen viejas
}
```
### Bien
```java
@PersistenceContext EntityManager em;

@Transactional
public void archiveOld(List<Long> ids) {
    int i = 0;
    for (Long id : ids) {
        em.find(Order.class, id).setStatus(Status.ARCHIVED); // dirty checking, sin save()
        if (++i % 50 == 0) {
            em.flush();
            em.clear();
        }
    }
}

@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update Order o set o.status = 'CANCELLED' where o.expiresAt < :now")
int cancelExpired(Instant now);
```

## Checklist de revisión
- [ ] Sin `save()` redundantes sobre entidades gestionadas.
- [ ] Procesos grandes con `flush()`/`clear()` por lote.
- [ ] `@Modifying` con `clearAutomatically`/`flushAutomatically` si se reutilizan entidades.
- [ ] `readOnly = true` en lecturas.
- [ ] Ninguna entidad gestionada compartida entre hilos.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de integración que verifica estado tras `@Modifying` | 2 | tests del proyecto generado (`db-testing`) |
| Revisión de procesos masivos | 3 | agente `code-reviewer` |

> Revisión humana: no hay regla estática fiable para esta materia.

## Relacionados, fuentes y mantenimiento
- Relacionados: `transactions`, `batching-and-bulk-ops`, `lazy-vs-eager`, `spring-data-rules`.
- Fuentes: guía de usuario de Hibernate ORM (persistence context, flushing) y Spring Data JPA reference (`@Modifying`) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
