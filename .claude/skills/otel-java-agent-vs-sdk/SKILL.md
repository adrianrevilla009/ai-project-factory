---
name: otel-java-agent-vs-sdk
description: "Usar al decidir cómo instrumentar un servicio Spring Boot con OpenTelemetry: agente Java, starter/SDK o puente Micrometer Tracing."
metadata:
  block: "10-observability-app"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# OpenTelemetry en Java: agente vs SDK

## Cuándo aplicar y cuándo no
- Aplica al elegir y configurar la instrumentación de un servicio Java/Spring Boot.
- No aplica a servicios que no son JVM ni a la definición de métricas de negocio (ver `metrics-micrometer`).

## Reglas
- **MUST** elegir UNA vía principal por servicio y documentarla en su README: (a) agente Java, (b) Micrometer Tracing + puente OTel, (c) SDK/starter de OTel.
- **SHOULD** preferir el agente Java por defecto: instrumenta JDBC, HTTP clients, Kafka y servlet sin tocar código, y se actualiza sin recompilar.
- **MUST NOT** combinar agente y puente Micrometer/OTel sobre los mismos spans: produce spans duplicados o trazas partidas.
- **MUST** fijar la versión del agente (no `latest`) y verificar su checksum al construir la imagen.
- **MUST** configurar el agente por variables `OTEL_*` (servicio, endpoint, muestreo), no por código.
- **SHOULD** usar la API de OTel (`io.opentelemetry.api`) o la Observation API de Spring para spans manuales de negocio, nunca el SDK interno.
- **MUST** probar el arranque con y sin agente en CI; el servicio debe funcionar si el Collector no responde.
- **MUST NOT** activar instrumentaciones que no se usan (reduce overhead y superficie).

## Por qué
El agente da cobertura amplia con coste mínimo, pero oculta qué se instrumenta y añade overhead de arranque; Micrometer Tracing encaja si el equipo ya vive en la Observation API de Spring y quiere control en código. Mezclarlos es el error habitual. El detalle de versiones y compatibilidad con Spring Boot debe verificarse en la documentación oficial (comprobar al fijar la versión).

## Ejemplos
### Mal
```dockerfile
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar /agent.jar
ENTRYPOINT ["java","-javaagent:/agent.jar","-jar","app.jar"]
# y además micrometer-tracing-bridge-otel en el pom: spans duplicados
```
### Bien
```dockerfile
# Versión y checksum fijados por ARG (valores de ejemplo: comprobar al fijar la versión)
ARG OTEL_AGENT_VERSION=changeme
ARG OTEL_AGENT_SHA256=changeme
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v${OTEL_AGENT_VERSION}/opentelemetry-javaagent.jar /opt/otel/agent.jar
RUN echo "${OTEL_AGENT_SHA256}  /opt/otel/agent.jar" | sha256sum -c -
ENV JAVA_TOOL_OPTIONS="-javaagent:/opt/otel/agent.jar" \
    OTEL_SERVICE_NAME=orders-api \
    OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector.observability:4317 \
    OTEL_TRACES_SAMPLER=parentbased_traceidratio \
    OTEL_TRACES_SAMPLER_ARG=0.1
```

## Checklist de revisión
- [ ] Una sola vía de instrumentación declarada.
- [ ] Agente con versión y checksum fijados.
- [ ] Configuración por `OTEL_*`.
- [ ] El servicio arranca si el Collector no está disponible.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de Dockerfile y dependencias (agente + bridge a la vez) | 3 | agente `code-reviewer` |
| Regla Conftest sobre Dockerfile con `latest` (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `otel-fundamentals-and-semconv`, `tracing`, `metrics-micrometer`, `container-images`, `jvm-in-containers`.
- Fuentes: documentación oficial de OpenTelemetry Java y de Spring Boot (observability); versiones (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
