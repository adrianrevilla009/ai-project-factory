---
name: metrics-micrometer
description: "Usar al crear o revisar métricas de aplicación con Micrometer en Spring Boot: nombres, tags, cardinalidad, histogramas y exposición Prometheus."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Métricas con Micrometer

## Cuándo aplicar y cuándo no
- Aplica a contadores, timers, gauges y summaries propios, y a la configuración de Actuator/Prometheus.
- No aplica a métricas de JVM (ver `jvm-observability`) ni a la definición de alertas (`alerting-symptom-based`).

## Reglas
- **MUST** inyectar `MeterRegistry`; **MUST NOT** usar `Metrics.globalRegistry` salvo en librerías sin Spring.
- **MUST** nombrar en minúsculas con puntos (`orders.created`); Micrometer lo traduce al formato de cada backend.
- **MUST NOT** usar como tag valores no acotados: IDs, emails, URLs con parámetros, mensajes de excepción.
- **MUST** mantener tags de un conjunto cerrado y conocido (estado, canal, tipo de error); documentar el conjunto.
- **MUST** medir latencia con `Timer` (no con gauge ni contador de ms) y habilitar histogramas para SLO en los endpoints críticos.
- **SHOULD** usar `@Timed`/Observation API para handlers, y registrar el meter una vez (campo), no en cada llamada con tags dinámicos.
- **SHOULD** añadir tags comunes (`application`, `region`) con `management.metrics.tags.*`, no a mano.
- **MUST** exponer solo `health` y `prometheus` (y lo estrictamente necesario) en `management.endpoints.web.exposure.include`, en puerto/ruta de gestión no público.
- **MUST NOT** registrar métricas dentro de bucles calientes creando meters nuevos por iteración.

## Por qué
Cada combinación distinta de tags crea una serie temporal; un `userId` como tag puede disparar memoria y coste del backend. Los histogramas permiten calcular percentiles agregables entre instancias (los percentiles precalculados en cliente no se pueden agregar). Propiedades exactas: TODO-VERIFY contra la versión de Spring Boot/Micrometer del proyecto.

## Ejemplos
### Mal
```java
Counter.builder("orders")
    .tag("customer", order.getCustomerEmail())   // cardinalidad ilimitada
    .register(registry).increment();
```
### Bien
```java
@Component
class OrderMetrics {
    private final Counter created;
    private final MeterRegistry registry;

    OrderMetrics(MeterRegistry registry) {
        this.registry = registry;
        this.created = Counter.builder("orders.created")
            .description("Orders accepted")
            .tag("channel", "web")
            .register(registry);
    }

    void recordCreated() { created.increment(); }

    void recordFailure(FailureReason reason) {  // enum cerrado
        registry.counter("orders.failed", "reason", reason.name().toLowerCase()).increment();
    }
}
```
```yaml
management:
  endpoints.web.exposure.include: health,prometheus
  metrics:
    tags.application: orders-api
    distribution.percentiles-histogram.http.server.requests: true
```

## Checklist de revisión
- [ ] Ningún tag con valores no acotados.
- [ ] Latencias como `Timer` con histograma donde hay SLO.
- [ ] Exposición de Actuator mínima.
- [ ] Meters creados una vez.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Semgrep: tag de métrica con valor de identificador (heurística, no ejecutada) | 1 | `policies/semgrep/java-metrics-cardinality.yaml` |
| Revisión de nombres y tags | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `otel-fundamentals-and-semconv`, `golden-signals-red-use`, `slo-sli-error-budgets`, `actuator-and-health`.
- Fuentes: documentación oficial de Micrometer y Spring Boot Actuator (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
