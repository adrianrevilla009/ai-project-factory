---
name: reactive-vs-blocking
description: Usar al decidir entre Spring MVC bloqueante (con hilos virtuales) y WebFlux reactivo para un servicio nuevo, o al mezclar ambos modelos.
metadata:
  block: "04-spring-platform"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "human"
---

# Reactivo vs bloqueante

## Cuándo aplicar y cuándo no
- Aplica al elegir stack de un servicio, al añadir `spring-boot-starter-webflux` o al introducir `Mono`/`Flux`.
- No aplica a servicios ya reactivos de punta a punta que solo añaden endpoints.

## Reglas
- **MUST** por defecto usar Spring MVC bloqueante (Java + Spring Boot + Maven); justificar WebFlux con un ADR del proyecto.
- **SHOULD** activar hilos virtuales (`spring.threads.virtual.enabled=true`, Boot 3.2+, requiere Java 21+; verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08) antes de plantear reactivo por escalabilidad de I/O.
- **MUST** elegir WebFlux solo con necesidad real: streaming/backpressure (SSE, WebSocket), fan-out masivo, o stack reactivo completo.
- **MUST NOT** mezclar JDBC/JPA bloqueante dentro de un pipeline reactivo; si hay JPA, el servicio es bloqueante.
- **MUST NOT** llamar a `.block()` en hilos del event loop.
- **MUST** envolver código bloqueante inevitable con `Schedulers.boundedElastic()`.
- **SHOULD** usar `WebClient` desde MVC solo para composición asíncrona puntual; para llamadas simples usar `RestClient`.
- **MUST** que el equipo conozca depuración y testing reactivos (`StepVerifier`) antes de adoptarlo.

## Por qué
El modelo reactivo cuesta legibilidad, trazas de pila, depuración y contexto (MDC, seguridad, transacciones). Los hilos virtuales cubren el caso típico de muchas peticiones esperando I/O con código imperativo. Reactivo compensa cuando hay backpressure o streaming reales. Una sola llamada bloqueante en el event loop degrada todo el servicio.

## Ejemplos
### Mal
```java
@GetMapping("/orders/{id}")
Mono<OrderDto> get(@PathVariable UUID id) {
    Order o = orderRepository.findById(id).orElseThrow(); // JPA bloqueante en el event loop
    return Mono.just(mapper.toDto(o));
}
```
### Bien (bloqueante con hilos virtuales)
```yaml
spring:
  threads:
    virtual:
      enabled: true
```
```java
@GetMapping("/orders/{id}")
OrderDto get(@PathVariable UUID id) {
    return mapper.toDto(orderRepository.findById(id).orElseThrow(OrderNotFoundException::new));
}
```

## Checklist de revisión
- [ ] Hay justificación escrita si se usa WebFlux.
- [ ] No hay JPA/JDBC dentro de pipelines reactivos.
- [ ] No hay `.block()` en código reactivo.
- [ ] Hilos virtuales evaluados antes de reactivo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana de la decisión de stack (ADR del proyecto) | 4 | gate de arquitectura |
| Regla Semgrep: `.block()` en clases con `Mono`/`Flux` | 1 | pendiente |

> Estado: revisión humana; sin artefacto automático todavía.

## Relacionados, fuentes y mantenimiento
- Relacionados: `http-clients-and-timeouts`, `spring-data-rules`, `testing-slices`.
- Fuentes: Spring Framework Reference (Web MVC / WebFlux), Spring Boot Reference (hilos virtuales).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
