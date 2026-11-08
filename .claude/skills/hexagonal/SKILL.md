---
name: hexagonal
description: Usar al estructurar un servicio Spring Boot con puertos y adaptadores para aislar el dominio de web, base de datos y mensajería.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Arquitectura hexagonal (puertos y adaptadores)

## Cuándo aplicar y cuándo no
- Aplica a servicios con lógica de negocio no trivial y varias fuentes de entrada/salida (REST, Kafka, JPA, clientes HTTP).
- No aplica a CRUD puro sin reglas de dominio, scripts o jobs triviales: el coste de puertos y mapeos no se amortiza.

## Reglas
- **MUST** separar paquetes `domain`, `application` y `adapter` (`adapter.in.web`, `adapter.out.persistence`...).
- **MUST** que `domain` no importe Spring, JPA, Jackson ni nada de `adapter`.
- **MUST** definir los puertos de salida (`OrderRepository`, `PaymentGateway`) como interfaces en `application` o `domain`; los adaptadores los implementan.
- **MUST** exponer casos de uso como puertos de entrada (`PlaceOrderUseCase`) invocados por los adaptadores de entrada.
- **MUST NOT** devolver entidades JPA ni DTOs HTTP desde el dominio; mapear en el adaptador.
- **SHOULD** una entidad JPA separada del modelo de dominio cuando el modelo de persistencia distorsione el dominio; aceptar la entidad como modelo solo en servicios simples y decidirlo por escrito.
- **SHOULD** que los tests del dominio no necesiten contexto Spring.
- **MUST NOT** usar Lombok (D27); usar `record` y constructores explícitos.

## Por qué
El dominio cambia por razones de negocio; los adaptadores, por razones tecnológicas. Invertir la dependencia permite testear reglas sin infraestructura y sustituir Kafka, JPA o un cliente HTTP sin tocar el núcleo. El precio es más clases y mapeos: se paga solo cuando hay dominio que proteger.

## Ejemplos
### Mal
```java
@Service
class OrderService {
    @Autowired JpaOrderRepository repo;          // dominio atado a JPA
    ResponseEntity<OrderJson> place(OrderJson in) { /* reglas + HTTP + SQL mezclados */ }
}
```
### Bien
```java
// application
public interface PlaceOrderUseCase { OrderId place(PlaceOrderCommand cmd); }
public interface OrderRepository { void save(Order order); }

// application (sin anotaciones de framework en domain)
class PlaceOrderService implements PlaceOrderUseCase {
    private final OrderRepository orders;
    PlaceOrderService(OrderRepository orders) { this.orders = orders; }
    public OrderId place(PlaceOrderCommand cmd) {
        Order order = Order.create(cmd.customerId(), cmd.lines());
        orders.save(order);
        return order.id();
    }
}

// adapter.out.persistence
@Repository
class JpaOrderRepositoryAdapter implements OrderRepository {
    private final SpringDataOrderRepository jpa;
    JpaOrderRepositoryAdapter(SpringDataOrderRepository jpa) { this.jpa = jpa; }
    public void save(Order order) { jpa.save(OrderEntity.from(order)); }
}
```

## Checklist de revisión
- [ ] `domain` no importa `org.springframework`, `jakarta.persistence` ni `adapter`.
- [ ] Cada dependencia externa tiene un puerto y un adaptador.
- [ ] Los controladores solo traducen HTTP a comando y llaman al caso de uso.
- [ ] Los tests de dominio corren sin Spring.
- [ ] Si no hay separación de modelo de persistencia, hay una nota de decisión.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Reglas ArchUnit de dominio sin frameworks y capas | 1 | `policies/archunit/HexagonalArchitectureRules.java` (ejemplo para copiar al proyecto generado) |
| Revisión de diseño | 3 | agente de revisión de arquitectura (pendiente) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `clean-architecture`, `layering-rules-archunit`, `ddd-tactical`, `anti-corruption-layer`.
- Fuentes: Alistair Cockburn, "Hexagonal Architecture" (alistair.cockburn.us) — comprobar URL exacta; ArchUnit User Guide (archunit.org) — comprobar versión.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
