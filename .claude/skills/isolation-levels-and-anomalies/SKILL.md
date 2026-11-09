---
name: isolation-levels-and-anomalies
description: "Usar al razonar sobre concurrencia en BD: niveles de aislamiento, anomalías (lost update, write skew) y cuándo subir el nivel."
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Niveles de aislamiento y anomalías

## Cuándo aplicar y cuándo no
- Aplica a casos de uso con lectura-decisión-escritura sobre datos compartidos (saldos, stock, cupos, reservas).
- No aplica a escrituras independientes sin lectura previa ni a lecturas aproximadas (informes).

## Reglas
- **MUST** conocer el nivel por defecto del motor de producción (PostgreSQL: READ COMMITTED; MySQL/InnoDB: REPEATABLE READ) y no asumir que es igual en todos.
- **MUST** identificar las anomalías posibles de cada caso de uso: lost update, non-repeatable read, phantom, write skew.
- **MUST** proteger el patrón "leer y luego escribir según lo leído" con bloqueo (`optimistic-locking`/`pessimistic-locking`), una restricción de BD o un `UPDATE` atómico condicional; no confiar en el aislamiento por defecto.
- **SHOULD** preferir restricciones declarativas (`UNIQUE`, `CHECK`, FK) como última defensa de invariantes.
- **SHOULD** usar `UPDATE ... SET stock = stock - :n WHERE id = :id AND stock >= :n` en lugar de leer, restar y guardar.
- **MUST** reintentar las transacciones abortadas por fallos de serialización o deadlock (SQLSTATE `40001`/`40P01` en PostgreSQL) si se usa `SERIALIZABLE` o bloqueos.
- **MUST NOT** subir globalmente a `SERIALIZABLE` como "solución"; hacerlo solo por caso de uso, con reintentos y medición.
- **MUST** documentar el nivel elegido junto al `@Transactional(isolation = ...)`.

## Por qué
READ COMMITTED permite que dos transacciones lean el mismo saldo y ambas escriban: una pisa a la otra sin error. Cada nivel superior reduce anomalías a cambio de más conflictos o bloqueos; la decisión debe ser consciente y local.

## Ejemplos
### Mal
```java
@Transactional
public void reserve(Long itemId, int qty) {
    Item item = items.findById(itemId).orElseThrow();
    if (item.getStock() >= qty) {          // otra transacción puede haber reservado entre medias
        item.setStock(item.getStock() - qty);
    }
}
```
### Bien
```java
interface ItemRepository extends JpaRepository<Item, Long> {
    @Modifying
    @Query("update Item i set i.stock = i.stock - :qty where i.id = :id and i.stock >= :qty")
    int decrementIfAvailable(Long id, int qty);
}

@Transactional
public void reserve(Long itemId, int qty) {
    if (items.decrementIfAvailable(itemId, qty) == 0) {
        throw new OutOfStockException(itemId);
    }
}
```
```sql
ALTER TABLE items ADD CONSTRAINT stock_non_negative CHECK (stock >= 0);
```

## Criterios de decisión y trampas
### Cómo decidir
- Parte del nivel por defecto del motor y razona qué anomalías (lectura sucia, no repetible, fantasma, escritura sesgada) importan en cada caso.
- Sube el nivel o usa bloqueos explícitos solo donde una invariante lo exige.
### Trampas frecuentes
- Asumir que «serializable» está activado.
- Creer que dos lecturas seguidas dan lo mismo.
- Invariantes entre filas protegidas solo por el nivel de aislamiento por defecto.
- Subir el aislamiento de todo el sistema por miedo.
- No reintentar los fallos de serialización.
### Evidencia
- Una prueba concurrente reproduce la anomalía que se teme y demuestra que está evitada.

## Checklist de revisión
- [ ] Se sabe el nivel real del motor y la versión.
- [ ] Cada read-modify-write está protegido (UPDATE atómico, versión, lock o constraint).
- [ ] Invariantes críticas respaldadas por constraints.
- [ ] Reintento definido ante fallo de serialización/deadlock.
- [ ] Nivel elevado solo con justificación.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Test de concurrencia con hilos sobre BD real (Testcontainers) | 2 | pendiente (`db-testing`, `concurrency-testing`) |
| Revisión de casos de uso con read-modify-write | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `transactions`, `optimistic-locking`, `pessimistic-locking`, `concurrency-testing`, `idempotency-and-deduplication`.
- Fuentes: documentación del motor elegido (p. ej. PostgreSQL, "Transaction Isolation").
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
