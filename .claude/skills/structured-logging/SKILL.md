---
name: structured-logging
description: "Usar al configurar logs JSON, correlación con trace_id y envío a Loki en servicios Spring Boot; complementa logging-rules."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Logging estructurado y correlación

## Cuándo aplicar y cuándo no
- Aplica a la configuración del formato de log, el MDC, la correlación con trazas y el envío a Loki.
- No aplica a niveles ni a qué mensajes escribir (ver `logging-rules`) ni a eventos de auditoría (`audit-trail-and-security-logging`).

## Reglas
- **MUST** emitir logs a stdout en JSON, una línea por evento; el agente de la plataforma los recoge. **MUST NOT** escribir ficheros de log dentro del contenedor.
- **MUST** incluir `timestamp` (UTC, ISO-8601), `level`, `logger`, `message`, `service.name`, `trace_id` y `span_id`.
- **MUST** propagar la correlación vía MDC o integración de OTel/Micrometer, y limpiar el MDC al terminar tareas asíncronas (ver `async-and-context-propagation`).
- **MUST NOT** incluir PII, secretos ni cuerpos completos; aplicar enmascarado en el encoder o en el Collector.
- **MUST NOT** usar etiquetas de Loki de alta cardinalidad (`trace_id`, `user_id`); las etiquetas son pocas (`service`, `namespace`, `level`) y el resto se filtra por contenido.
- **SHOULD** registrar una sola vez cada error, con la excepción como último argumento.
- **SHOULD** usar el soporte nativo de logging estructurado de Spring Boot si la versión lo ofrece (comprobar desde qué versión y formatos), o un encoder JSON explícito.
- **SHOULD** definir un campo `event` estable en eventos de negocio para poder consultarlos y alertar.

## Por qué
Los logs en texto libre obligan a regex frágiles; el JSON permite consultas y paneles fiables. Etiquetas de Loki con muchos valores degradan el índice. Sin `trace_id` el salto de una alerta a la causa raíz es manual.

## Ejemplos
### Mal
```xml
<!-- logback.xml: texto libre, a fichero, sin correlación -->
<appender name="F" class="ch.qos.logback.core.FileAppender">
  <file>/var/log/app.log</file>
  <encoder><pattern>%d %-5level %msg%n</pattern></encoder>
</appender>
```
### Bien
```yaml
# application.yml (`logging.structured.format.console`; verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08)
logging:
  structured:
    format:
      console: ecs
```
```json
{"@timestamp":"2026-11-07T10:15:30Z","log.level":"INFO","message":"order paid","service.name":"orders-api","trace_id":"4bf92f3577b34da6a3ce929d0e0e4736","span_id":"00f067aa0ba902b7","event":"order.paid"}
```
```yaml
# Promtail/Alloy: pocas etiquetas
labels: { service: orders-api, namespace: shop }
```

## Checklist de revisión
- [ ] Salida JSON a stdout, sin ficheros.
- [ ] `trace_id` y `span_id` presentes en los logs de petición.
- [ ] Etiquetas de Loki acotadas.
- [ ] Sin PII ni secretos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Semgrep: `System.out`, `printStackTrace`, concatenación en logs | 1 | `policies/semgrep/java-logging.yaml` |
| Revisión de config de logback/Loki | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `logging-rules`, `tracing`, `pii-and-data-classification`, `async-and-context-propagation`.
- Fuentes: documentación oficial de Spring Boot (logging) y Grafana Loki (labels) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
