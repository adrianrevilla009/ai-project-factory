---
name: project-layout
description: Usar al crear un servicio Spring Boot o añadir paquetes/módulos; define estructura por módulos de negocio con Spring Modulith.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Estructura de proyecto con Spring Modulith

## Cuándo aplicar y cuándo no
- Aplica a cualquier servicio Spring Boot (Java + Maven) nuevo o a la creación de un módulo de negocio.
- No aplica a librerías sin Spring ni a la decisión monolito vs microservicios (ver `modular-monolith`, `microservices-decision-guide`).

## Reglas
- **MUST** organizar el código por módulo de negocio (`order`, `billing`, `customer`), no por capa técnica global (`controller/`, `service/`, `repository/`).
- **MUST** colocar cada módulo como subpaquete directo del paquete raíz de la aplicación; la clase `@SpringBootApplication` vive en el paquete raíz.
- **MUST** exponer solo la API del módulo en su paquete raíz (servicio de aplicación, DTOs, eventos); lo demás va en subpaquetes internos (`internal`).
- **MUST NOT** acceder a clases internas de otro módulo ni crear dependencias cíclicas entre módulos.
- **MUST** incluir un test que ejecute `ApplicationModules.of(Application.class).verify()`.
- **SHOULD** comunicar módulos mediante eventos (ver `domain-events-in-spring`) cuando no se necesite respuesta síncrona.
- **SHOULD** dentro de cada módulo separar `web`, `application`, `domain`, `infrastructure` solo si el módulo lo justifica; no crear capas vacías.
- **MUST NOT** usar Lombok (D27); usar `record` y constructores explícitos.

## Por qué
Una estructura por capa técnica hace que todo dependa de todo y el cambio de una funcionalidad toque cuatro paquetes. Los módulos con límites verificados permiten evolucionar a servicios separados solo si hace falta. `verify()` convierte la convención en un test que falla.

## Ejemplos
### Mal
```text
com.acme.shop
  controller/OrderController.java, CustomerController.java
  service/OrderService.java, CustomerService.java
  repository/OrderRepository.java, CustomerRepository.java
```
### Bien
```text
com.acme.shop
  ShopApplication.java
  order/            OrderService.java, OrderCreated.java   (API del módulo)
  order/internal/   OrderController.java, OrderRepository.java, Order.java
  customer/         CustomerService.java
  customer/internal/...
```
```java
class ModularityTests {
    @Test
    void verifyModuleStructure() {
        ApplicationModules.of(ShopApplication.class).verify();
    }
}
```
Requiere la dependencia `spring-modulith-core`.

## Criterios de decisión y trampas
### Cómo decidir
- Organiza por capacidad de negocio (paquetes por funcionalidad) y dentro de cada una, la separación entre dominio, aplicación e infraestructura que fije la arquitectura.
- Un módulo Maven por límite que realmente quieres hacer cumplir; más módulos no es mejor.
### Trampas frecuentes
- Paquetes por tipo técnico (`controllers`, `services`) que dispersan una funcionalidad.
- Dependencias cíclicas entre paquetes.
- Un módulo «common» que lo acoge todo.
- Mover paquetes sin pruebas de arquitectura.
- Clases públicas que deberían ser internas.
### Evidencia
- Pruebas de arquitectura que fallan ante dependencias prohibidas.

## Checklist de revisión
- [ ] Paquetes de primer nivel = módulos de negocio.
- [ ] Nada fuera de la API del módulo es accesible desde otros módulos.
- [ ] Existe el test `verify()` y pasa.
- [ ] Sin ciclos entre módulos ni Lombok.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test `ApplicationModules.verify()` | 1 | tests del proyecto generado (patrón arriba) |
| Reglas ArchUnit de capas | 1 | `policies/archunit/` (pendiente) |
| Revisión de límites de módulo | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `modular-monolith`, `layering-rules-archunit`, `domain-events-in-spring`, `dependency-injection-rules`.
- Fuentes oficiales: documentación de Spring Modulith (docs.spring.io/spring-modulith).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
