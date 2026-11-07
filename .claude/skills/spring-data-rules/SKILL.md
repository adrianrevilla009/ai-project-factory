---
name: spring-data-rules
description: "Usar al escribir repositorios y transacciones con Spring Data JPA: límites transaccionales, queries explícitas, open-in-view desactivado."
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Reglas de Spring Data

## Cuándo aplicar y cuándo no
- Aplica a repositorios Spring Data JPA y a la gestión de transacciones en servicios.
- No aplica al diseño de esquema ni de índices (ver bloque 03) ni a jOOQ/JDBC (ver `jdbc-and-jooq`).

## Reglas
- **MUST** definir `@Transactional` en la capa de servicio de aplicación, nunca en controladores ni repositorios.
- **MUST** marcar las lecturas con `@Transactional(readOnly = true)`.
- **MUST** fijar `spring.jpa.open-in-view=false`.
- **MUST** usar `Pageable` con tamaño máximo acotado en listados; **MUST NOT** devolver `findAll()` sin límite en endpoints.
- **MUST NOT** devolver entidades fuera del servicio; devolver DTOs o proyecciones (ver `mapping-mapstruct`).
- **MUST** cargar relaciones de forma explícita (ver `n-plus-one`).
- **SHOULD** usar `@Query` explícita cuando el nombre derivado supere ~3 condiciones; los nombres largos son frágiles.
- **MUST NOT** llamar a métodos `@Transactional` de la misma clase (auto-invocación): el proxy no se aplica.
- **MUST NOT** hacer llamadas HTTP lentas dentro de una transacción abierta.
- **SHOULD** usar `@Modifying` con consultas de actualización masiva y `clearAutomatically` solo si se entiende el efecto en el contexto de persistencia.

## Por qué
Transacciones en el borde del caso de uso dan atomicidad coherente. Con open-in-view activo, las consultas perezosas se ejecutan en la capa web, ocultan N+1 y mantienen conexiones ocupadas durante la serialización. Los proxies de Spring solo interceptan llamadas externas.

## Ejemplos
### Mal
```java
@RestController
class OrderController {
    @Transactional                                   // transacción en el controlador
    @GetMapping("/orders")
    List<Order> all() { return orderRepository.findAll(); } // entidades y sin límite
}
```
### Bien
```java
interface OrderRepository extends JpaRepository<Order, Long> {
    @Query("select o from Order o where o.status = :status")
    Page<Order> findByStatus(OrderStatus status, Pageable pageable);
}

@Service
class OrderQueryService {
    private final OrderRepository repository;
    private final OrderMapper mapper;

    OrderQueryService(OrderRepository repository, OrderMapper mapper) {
        this.repository = repository;
        this.mapper = mapper;
    }

    @Transactional(readOnly = true)
    Page<OrderSummary> list(OrderStatus status, Pageable pageable) {
        return repository.findByStatus(status, pageable).map(mapper::toSummary);
    }
}
```
```yaml
spring:
  jpa:
    open-in-view: false
  data:
    web:
      pageable:
        max-page-size: 100
```

## Checklist de revisión
- [ ] `@Transactional` solo en servicios; lecturas `readOnly`.
- [ ] `open-in-view: false` y tamaño máximo de página.
- [ ] Sin entidades fuera del servicio ni auto-invocación transaccional.
- [ ] Sin I/O remoto lento dentro de la transacción.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep (EAGER en asociaciones ToOne) | 1 | `policies/semgrep/jpa-eager-toone.yaml` |
| Regla ArchUnit: `@Transactional` solo en servicios | 1 | `policies/archunit/` (pendiente) |
| Revisión de transacciones | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `n-plus-one`, `mapping-mapstruct`, `pagination-filter-sort`, `http-clients-and-timeouts`.
- Fuentes oficiales: Spring Data JPA Reference y Spring Framework "Transaction Management", consultadas 2026-11-07; TODO-VERIFY propiedades de paginación en la versión vigente.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
