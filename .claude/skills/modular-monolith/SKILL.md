---
name: modular-monolith
description: Usar al estructurar un sistema como un único despliegue con módulos de negocio aislados antes de (o en lugar de) separar en microservicios.
metadata:
  block: "05-architecture"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Monolito modular

## Cuándo aplicar y cuándo no
- Aplica por defecto a sistemas nuevos o equipos pequeños/medianos: un despliegue, fronteras de módulo estrictas.
- No aplica si hay requisitos demostrados de escalado, ciclo de despliegue o tecnología independientes por módulo (ver `microservices-decision-guide`).

## Reglas
- **MUST** dividir por capacidad de negocio (`orders`, `billing`), no por capa técnica.
- **MUST** que cada módulo exponga una API pública (interfaz/paquete `api`) y oculte su interior (`internal`).
- **MUST NOT** acceder a tablas o repositorios de otro módulo; comunicar por API del módulo o eventos de dominio.
- **MUST NOT** hacer joins SQL ni claves foráneas entre esquemas de módulos distintos.
- **MUST** que no haya ciclos entre módulos.
- **SHOULD** un esquema (o prefijo de tablas) por módulo en la misma base de datos, con propiedad clara.
- **SHOULD** comunicar efectos secundarios entre módulos con eventos internos (ver `domain-events-in-spring`).
- **MAY** usar Spring Modulith para verificar y documentar módulos.

## Por qué
Se obtienen fronteras evolutivas sin el coste operativo de la red: transacciones locales, un solo pipeline, depuración sencilla. Si las fronteras son reales, extraer un módulo a servicio es mecánico; si no, un microservicio solo reparte el barro.

## Ejemplos
### Mal
```java
package com.example.billing;
import com.example.orders.internal.OrderEntity;   // acceso al interior de otro módulo

class InvoiceService {
    Invoice create(Long id) { return fromOrder(orderJpaRepo.findById(id).get()); }
}
```
### Bien
```java
package com.example.orders.api;
public interface OrderQueries { OrderSummary summary(OrderId id); }

package com.example.billing.internal;
class InvoiceService {
    private final OrderQueries orders;               // solo la API pública
    InvoiceService(OrderQueries orders) { this.orders = orders; }
    Invoice create(OrderId id) { return Invoice.from(orders.summary(id)); }
}
```

## Checklist de revisión
- [ ] Los módulos siguen capacidades de negocio.
- [ ] Solo se usa `..api..` entre módulos; `..internal..` es privado.
- [ ] Sin ciclos ni acceso cruzado a tablas.
- [ ] Hay regla de arquitectura ejecutable.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| ArchUnit: internos inaccesibles y módulos sin ciclos | 1 | `policies/archunit/ModuleBoundaryRules.java` |
| Revisión de acceso cruzado a datos | 3 | revisión de PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `microservices-decision-guide`, `layering-rules-archunit`, `domain-events-in-spring`, `ddd-strategic`.
- Fuentes: documentación de Spring Modulith (spring.io/projects/spring-modulith) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
