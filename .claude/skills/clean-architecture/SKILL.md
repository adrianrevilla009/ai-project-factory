---
name: clean-architecture
description: Usar al decidir la dirección de dependencias entre entidades, casos de uso, adaptadores y frameworks; complementa hexagonal.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Clean Architecture

## Cuándo aplicar y cuándo no
- Aplica al diseñar el núcleo de un servicio con reglas de negocio de larga vida y al revisar si las dependencias apuntan hacia dentro.
- No aplica como plantilla de carpetas para todo: en servicios pequeños basta `hexagonal` simplificado. No sustituye a DDD.

## Reglas
- **MUST** que las dependencias de código fuente apunten solo hacia dentro: frameworks/adaptadores -> casos de uso -> entidades.
- **MUST** que las entidades y casos de uso no conozcan HTTP, SQL, Kafka ni el contenedor de Spring.
- **MUST** pasar datos entre fronteras como estructuras simples (`record`), no entidades JPA ni objetos de framework.
- **MUST** que cada caso de uso tenga una intención única (`CancelOrder`), no servicios "Manager" genéricos.
- **SHOULD** que el `main`/configuración Spring sea el único lugar que conoce todas las implementaciones (composición).
- **SHOULD** limitar el número de círculos al necesario (entidades, casos de uso, adaptadores); no crear capas vacías.
- **MUST NOT** introducir una capa solo para delegar (`ServiceImpl` que llama a otro `Service` sin lógica).

## Por qué
La regla de dependencia es lo único innegociable; los nombres de los círculos son orientativos. Hexagonal y Clean describen la misma inversión desde ángulos distintos: aquí se usa Clean para razonar sobre la dirección de dependencias y los modelos que cruzan fronteras.

## Ejemplos
### Mal
```java
// caso de uso conoce la web y la persistencia
class CancelOrder {
    ResponseEntity<?> handle(HttpServletRequest req, EntityManager em) { ... }
}
```
### Bien
```java
public record CancelOrderCommand(OrderId orderId, String reason) {}

public final class CancelOrder {
    private final OrderRepository orders;
    private final Clock clock;
    public CancelOrder(OrderRepository orders, Clock clock) { this.orders = orders; this.clock = clock; }

    public void execute(CancelOrderCommand cmd) {
        Order order = orders.findById(cmd.orderId()).orElseThrow(OrderNotFound::new);
        order.cancel(cmd.reason(), clock.instant());   // regla en la entidad
        orders.save(order);
    }
}
```

## Criterios de decisión y trampas
### Cómo decidir
- Úsala como criterio de dirección de dependencias (hacia el dominio), no como un número fijo de capas.
- El caso de uso es la unidad: una entrada, una salida y sus reglas.
### Trampas frecuentes
- Capas obligatorias que no aportan nada en servicios pequeños.
- Casos de uso que son simples reenvíos al repositorio.
- Modelos distintos por capa copiados campo a campo sin necesidad.
- Dependencias del framework en el núcleo.
- Confundir la estructura de carpetas con la arquitectura.
### Evidencia
- Un diagrama de dependencias real (no el deseado) coincide con las reglas.

## Checklist de revisión
- [ ] Ningún import apunta hacia fuera (entidades -> casos de uso -> adaptadores).
- [ ] Los límites usan `record`/DTO propios.
- [ ] No hay clases `*Manager`/`*Helper` con responsabilidades mezcladas.
- [ ] Cada capa existente aporta algo; no hay delegación vacía.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| ArchUnit: dominio sin frameworks y regla de capas | 1 | `policies/archunit/HexagonalArchitectureRules.java` |
| Revisión de diseño | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `hexagonal`, `layering-rules-archunit`, `solid`, `ddd-tactical`.
- Fuentes: Robert C. Martin, "The Clean Architecture" (blog.cleancoder.com, 2012).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
