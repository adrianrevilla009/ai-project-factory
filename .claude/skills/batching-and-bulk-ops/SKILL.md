---
name: batching-and-bulk-ops
description: Usar al insertar, actualizar o borrar muchas filas con JPA/JDBC, o al configurar jdbc batch_size, bulk JPQL y procesos por lotes.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Batching y operaciones masivas

## Cuándo aplicar y cuándo no
- Aplica a importaciones, cargas masivas, migraciones de datos, purgas y cualquier bucle que haga `save()` N veces.
- No aplica a escrituras de una sola entidad por petición ni a lecturas masivas (ver `projections-and-dtos`, `pagination`).

## Reglas
- **MUST** activar batching de JDBC explícitamente: `spring.jpa.properties.hibernate.jdbc.batch_size` (p. ej. 50) junto con `order_inserts=true` y `order_updates=true`.
- **MUST** recordar que `GenerationType.IDENTITY` desactiva el batching de inserts en Hibernate; usar `SEQUENCE` con `allocationSize` coherente (ver `id-generation`).
- **MUST** procesar cargas grandes en trozos (chunks) con una transacción por trozo y `flush()` + `clear()` del `EntityManager` al final de cada uno.
- **MUST** usar `@Modifying` JPQL/SQL (bulk) para actualizaciones/borrados masivos uniformes, sabiendo que saltan el contexto de persistencia: `clearAutomatically = true`.
- **MUST NOT** hacer `deleteAll()` o `findAll()` + bucle para borrar/actualizar miles de filas.
- **MUST NOT** cargar todo el resultado en memoria; usar paginación por clave (keyset) o `Stream` dentro de transacción de solo lectura.
- **SHOULD** usar `JdbcTemplate.batchUpdate` o jOOQ batch cuando no se necesite el modelo de entidades (ver `jdbc-and-jooq`).
- **SHOULD** hacer los procesos reanudables e idempotentes (marca de progreso por chunk).
- **SHOULD** medir con el conteo de sentencias/batches, no a ojo.

## Por qué
Cada `save` en un bucle puede ser un viaje de red; con `IDENTITY` Hibernate debe ejecutar el INSERT inmediatamente para conocer el id. El contexto de persistencia crece sin límite y el dirty checking se vuelve cuadrático. Un bulk update evita cargar entidades pero deja obsoletas las que ya estaban en memoria. Los valores de `batch_size` son punto de partida: medir (TODO-VERIFY propiedades contra la guía de usuario de Hibernate de la versión usada).

## Ejemplos
### Mal
```java
@Transactional
public void importAll(List<ProductRow> rows) {
    for (ProductRow r : rows) {
        productRepository.save(new Product(r.sku(), r.name())); // contexto crece, IDENTITY = 1 INSERT por fila
    }
}
```
### Bien
```java
public void importAll(List<ProductRow> rows) {
    for (List<ProductRow> chunk : Lists.partition(rows, 500)) {
        tx.executeWithoutResult(s -> {
            chunk.forEach(r -> entityManager.persist(new Product(r.sku(), r.name())));
            entityManager.flush();
            entityManager.clear();
        });
    }
}

@Modifying(clearAutomatically = true, flushAutomatically = true)
@Query("update Product p set p.active = false where p.lastSoldAt < :limit")
int deactivateStale(Instant limit);
```
```yaml
spring:
  jpa:
    properties:
      hibernate:
        jdbc.batch_size: 50
        order_inserts: true
        order_updates: true
```

## Checklist de revisión
- [ ] `batch_size` y `order_*` configurados y el id usa `SEQUENCE`.
- [ ] Cargas grandes en chunks con `flush()`/`clear()`.
- [ ] Borrados/updates masivos con query bulk, no con bucle.
- [ ] El proceso es reanudable y su transacción por chunk es corta.
- [ ] Hay una medición (sentencias o tiempo) que respalda el tamaño de lote.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep contra `deleteAll()`/`save` en bucle | 1 | pendiente (`policies/semgrep/`) |
| Revisión de procesos masivos | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `id-generation`, `persistence-context-and-flush`, `transactions`, `scheduling-and-batch`.
- Fuentes: guía de usuario de Hibernate ORM, capítulo de batching (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
