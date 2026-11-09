---
name: n-plus-one
description: Usar al escribir o revisar consultas JPA/Hibernate y mapeos de relaciones para evitar el problema N+1.
metadata:
  block: "03-persistence-sql"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# N+1 en JPA/Hibernate

## Cuándo aplicar y cuándo no
- Aplica a cualquier código que cargue entidades con asociaciones o recorra colecciones y acceda a relaciones.
- No aplica a consultas SQL nativas sin mapeo de asociaciones ni a procesos batch que ya usan proyecciones planas.

## Reglas
- **MUST** definir todas las asociaciones `@ManyToOne`/`@OneToOne` como `FetchType.LAZY` (el defecto EAGER es una causa habitual de N+1).
- **MUST** cargar lo necesario por caso de uso: `JOIN FETCH`, `@EntityGraph` o proyección a DTO.
- **MUST NOT** acceder a asociaciones perezosas dentro de bucles sin haberlas cargado.
- **MUST NOT** hacer `JOIN FETCH` de dos colecciones a la vez (producto cartesiano / `MultipleBagFetchException`); usar consultas separadas o `@BatchSize`.
- **SHOULD** preferir proyecciones DTO para lecturas de listados.
- **SHOULD** usar `hibernate.default_batch_fetch_size` como red de seguridad, no como sustituto del diseño.
- **MUST** cubrir las consultas críticas con un test que cuente sentencias SQL.
- **MUST NOT** activar `open-in-view` (`spring.jpa.open-in-view=false`).

## Por qué
Un listado de N pedidos con su cliente genera 1 + N consultas: invisible con 5 filas de demo, catastrófico con 50 000. La carga debe ser decisión explícita del caso de uso, no un efecto del mapeo. Verificar `FetchType` por defecto y propiedades contra la documentación vigente de Hibernate.

## Ejemplos
### Mal
```java
@Entity
class Order {
    @ManyToOne                    // EAGER por defecto
    private Customer customer;
}

List<Order> orders = orderRepository.findAll();
orders.forEach(o -> log.info(o.getCustomer().getName())); // 1 + N consultas
```
### Bien
```java
@Entity
class Order {
    @ManyToOne(fetch = FetchType.LAZY)
    private Customer customer;
}

interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("select o from Order o join fetch o.customer where o.status = :status")
    List<Order> findByStatusWithCustomer(OrderStatus status);

    @Query("select new com.acme.OrderSummary(o.id, c.name) from Order o join o.customer c")
    List<OrderSummary> findSummaries();
}
```
### Test que cuenta consultas
```java
@Test
void listOrders_executesSingleQuery() {
    var stats = sessionFactory.getStatistics();
    stats.clear();
    service.listOrdersWithCustomer();
    assertThat(stats.getPrepareStatementCount()).isEqualTo(1);
}
```
Requiere `hibernate.generate_statistics=true` en el perfil de test.

## Checklist de revisión
- [ ] Ninguna asociación `ToOne` es EAGER.
- [ ] Cada listado carga sus relaciones con fetch join, entity graph o DTO.
- [ ] No hay dos colecciones en el mismo fetch join.
- [ ] Hay test de conteo de queries en los casos críticos.
- [ ] `spring.jpa.open-in-view=false`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep: `@ManyToOne`/`@OneToOne` sin `fetch = LAZY` | 1 | `policies/semgrep/jpa-eager-toone.yaml` |
| Test que cuenta queries (patrón del ejemplo de arriba, que el proyecto generado debe incluir) | 1 | tests del proyecto generado |
| Hook `require-green-tests` al parar | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Revisión de consultas de listado | 3 | agente `code-reviewer` |

> Estado: la regla Semgrep existe; el hook `require_green_tests` existe en `.claude/hooks/stop/`.

## Relacionados, fuentes y mantenimiento
- Relacionados: `lazy-vs-eager`, `projections-and-dtos`, `joins-and-fetch-joins`, `testing-slices`.
- Fuentes: documentación de Hibernate ORM (guía de usuario, fetching).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
