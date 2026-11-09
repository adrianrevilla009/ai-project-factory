---
name: optimistic-locking
description: Usar al proteger entidades de actualizaciones concurrentes con @Version y al manejar OptimisticLockException.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Bloqueo optimista

## Cuándo aplicar y cuándo no
- Aplica a entidades editadas por varios usuarios/procesos con baja probabilidad de colisión.
- No aplica a contadores de alta contención (usar `UPDATE` atómico) ni a casos donde el conflicto debe esperar (ver `pessimistic-locking`).

## Reglas
- **MUST** añadir un atributo `@Version` (`long`/`Integer`/`Instant`; preferible numérico) a las entidades de agregado mutables compartidas.
- **MUST NOT** modificar el campo `@Version` a mano.
- **MUST** convertir `ObjectOptimisticLockingFailureException` (Spring) en una respuesta de conflicto (HTTP 409 Problem Details) o en reintento controlado.
- **MUST** reintentar solo operaciones idempotentes y con un tope de intentos (p. ej. 3) y espera con jitter; el reintento debe relanzar la transacción completa.
- **SHOULD** exponer la versión (ETag/`If-Match`) en APIs de edición para detectar conflictos entre peticiones HTTP separadas.
- **MUST NOT** capturar la excepción dentro de la misma transacción: el contexto queda inconsistente.
- **MUST** verificar que las actualizaciones masivas JPQL/SQL (`@Modifying`) incrementan la versión explícitamente (`update ... set version = version + 1`) o usar `versioned`; no lo hacen solas.
- **SHOULD** añadir la columna `version` en la migración con `NOT NULL DEFAULT 0`.

## Por qué
Sin versión, dos usuarios que editan el mismo registro producen un "lost update" silencioso. `@Version` añade `WHERE version = ?` al UPDATE y falla si cambió: detecta el conflicto sin retener bloqueos de BD.

## Ejemplos
### Mal
```java
@Entity
class Document {
    @Id Long id;
    String content;          // sin @Version: gana el último que guarda
}
```
### Bien
```java
@Entity
class Document {
    @Id Long id;
    String content;
    @Version private long version;
}

@ExceptionHandler(ObjectOptimisticLockingFailureException.class)
ProblemDetail onConflict(ObjectOptimisticLockingFailureException ex) {
    return ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT,
        "El recurso fue modificado por otro usuario; recargue y reintente.");
}
```
```sql
ALTER TABLE document ADD COLUMN version BIGINT NOT NULL DEFAULT 0;
```

## Checklist de revisión
- [ ] Entidades mutables compartidas con `@Version`.
- [ ] Conflicto mapeado a 409 o a reintento acotado.
- [ ] Reintento fuera de la transacción fallida.
- [ ] Updates masivos tratan la versión.
- [ ] Test de concurrencia que provoca el conflicto.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla ArchUnit: entidades de agregado raíz con `@Version` | 1 | pendiente (`policies/archunit/`) |
| Test de actualización concurrente | 2 | tests del proyecto generado (`db-testing`) |
| Revisión de modelo | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `pessimistic-locking`, `isolation-levels-and-anomalies`, `jpa-entity-design`, `error-handling-problem-details`.
- Fuentes: Jakarta Persistence (`@Version`) y Spring Framework (excepción de bloqueo optimista).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
