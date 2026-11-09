---
name: db-and-kafka-observability
description: "Usar al observar acceso a base de datos y Kafka desde la aplicación: latencia de queries, pool, lag de consumidores, reintentos y DLQ."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Observabilidad de BD y Kafka

## Cuándo aplicar y cuándo no
- Aplica a servicios que usan JDBC/JPA y productores/consumidores Kafka.
- No aplica a la monitorización del propio clúster Postgres o Kafka (operadores, bloque de Kubernetes).

## Reglas
- **MUST** exponer métricas del pool (`hikaricp.connections.active/pending/timeout`) y alertar por espera de conexión, que es síntoma de saturación.
- **MUST** tener spans de BD con `db.system.name` (estable en las convenciones semánticas de OpenTelemetry para spans de cliente de base de datos; verificado el 2026-11-08) y operación; **MUST NOT** guardar parámetros ni valores de la query en atributos.
- **SHOULD** habilitar logs de queries lentas con umbral configurable, sin parámetros; **SHOULD** contar sentencias por petición en tests (ver `n-plus-one`).
- **MUST** medir consumo Kafka con: lag por grupo/partición, tasa de procesamiento, tiempo de procesamiento por registro, errores y reintentos.
- **MUST** exponer métricas del cliente Kafka a Micrometer y propagar `traceparent` en cabeceras (ver `tracing`).
- **MUST** instrumentar la DLQ: contador de mensajes enviados a DLQ por tópico y motivo (conjunto cerrado) y alerta si crece (ver `dlq-retries-poison-messages`).
- **MUST NOT** usar clave de mensaje, ID de entidad ni nombre de consumidor efímero como tag.
- **SHOULD** medir el retraso extremo a extremo (timestamp del evento frente a procesado) para el SLI de frescura.
- **SHOULD** observar el outbox: filas pendientes y edad de la más antigua.

## Por qué
La mayoría de incidentes de datos se ven primero como espera de conexiones o lag creciente; el lag absoluto engaña, por eso importa su tendencia y la edad del mensaje. Los parámetros de query pueden contener PII.

## Ejemplos
### Mal
```java
span.setAttribute("db.statement", "select * from users where email='" + email + "'");
meterRegistry.counter("kafka.consumed", "key", record.key()).increment(); // cardinalidad
```
### Bien
```java
Timer.builder("orders.consumer.processing")
     .tag("topic", record.topic())
     .publishPercentileHistogram()
     .register(registry)
     .record(() -> handler.handle(record));

registry.counter("orders.dlq.sent", "topic", "orders.v1", "reason", "validation").increment();
```
```yaml
- alert: DbPoolWaiting
  expr: max by (pod) (hikaricp_connections_pending) > 0
  for: 5m
  labels: { severity: ticket }
```

## Checklist de revisión
- [ ] Pool de conexiones con métricas y alerta de espera.
- [ ] Spans de BD sin valores de parámetros.
- [ ] Lag, tiempo de proceso y DLQ visibles por tópico.
- [ ] Contexto de traza propagado en Kafka.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Semgrep de tags de alta cardinalidad (heurística) | 1 | `policies/semgrep/java-metrics-cardinality.yaml` |
| Revisión de dashboards y alertas de BD/Kafka | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `connection-pooling`, `kafka-producers-consumers`, `dlq-retries-poison-messages`, `n-plus-one`, `tracing`, `metrics-micrometer`.
- Fuentes: documentación oficial de Micrometer, Spring Kafka, HikariCP y OpenTelemetry semconv (database/messaging), consultada 2026-11-07.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
