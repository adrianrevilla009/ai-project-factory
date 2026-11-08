# Estándares · 10-observability-app

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## alerting-symptom-based

- **MUST** paginar solo por síntomas que afectan al usuario (errores, latencia, indisponibilidad, frescura de datos) o por consumo de presupuesto de error; las causas (CPU, heap, un pod caído) van a paneles o tickets.
- **MUST** que toda alerta paginable sea accionable, urgente y esté documentada: `summary`, `description` y `runbook_url` obligatorios.
- **MUST** definir `severity` con valores cerrados (`page`, `ticket`, `info`) y enrutar solo `page` a la guardia.
- **MUST** usar `for:` o ventanas multi-ventana para evitar flapping; **MUST NOT** alertar con `for: 0m` sobre métricas ruidosas.
- **SHOULD** usar alertas de burn rate multi-ventana sobre SLO (rápida y lenta) en vez de umbrales fijos de error.
- **SHOULD** agrupar e inhibir en Alertmanager (una caída de dependencia no debe disparar 30 alertas).
- **MUST** incluir una alerta de "latido" (watchdog) para detectar que el pipeline de alertas sigue vivo.
- **MUST** revisar trimestralmente las alertas que más disparan o que nunca actuaron; eliminar o degradar las ruidosas.
- **MUST NOT** enviar secretos ni datos personales en las anotaciones.

## db-and-kafka-observability

- **MUST** exponer métricas del pool (`hikaricp.connections.active/pending/timeout`) y alertar por espera de conexión, que es síntoma de saturación.
- **MUST** tener spans de BD con `db.system.name` (estable en las convenciones semánticas de OpenTelemetry para spans de cliente de base de datos; verificado el 2026-11-08) y operación; **MUST NOT** guardar parámetros ni valores de la query en atributos.
- **SHOULD** habilitar logs de queries lentas con umbral configurable, sin parámetros; **SHOULD** contar sentencias por petición en tests (ver `n-plus-one`).
- **MUST** medir consumo Kafka con: lag por grupo/partición, tasa de procesamiento, tiempo de procesamiento por registro, errores y reintentos.
- **MUST** exponer métricas del cliente Kafka a Micrometer y propagar `traceparent` en cabeceras (ver `tracing`).
- **MUST** instrumentar la DLQ: contador de mensajes enviados a DLQ por tópico y motivo (conjunto cerrado) y alerta si crece (ver `dlq-retries-poison-messages`).
- **MUST NOT** usar clave de mensaje, ID de entidad ni nombre de consumidor efímero como tag.
- **SHOULD** medir el retraso extremo a extremo (timestamp del evento frente a procesado) para el SLI de frescura.
- **SHOULD** observar el outbox: filas pendientes y edad de la más antigua.

## golden-signals-red-use

- **MUST** cubrir para cada servicio expuesto las señales RED: tasa de peticiones (Rate), errores (Errors) y duración (Duration) por endpoint (`http.route`, no URL cruda).
- **MUST** cubrir para cada recurso (CPU, memoria, pool de conexiones, cola, disco) el método USE: utilización, saturación y errores.
- **MUST** añadir saturación (colas, pool pendiente, lag) como cuarta señal dorada.
- **MUST** medir la latencia con histograma y mostrar percentiles (p50/p95/p99) calculados con `histogram_quantile`; **MUST NOT** promediar percentiles entre instancias.
- **MUST** separar errores de servidor (5xx, excepciones) de rechazos de cliente (4xx).
- **SHOULD** versionar los dashboards como código (JSON/Grafonnet/provisioning) con la misma plantilla para todos los servicios.
- **SHOULD** ordenar el dashboard de arriba abajo: SLO y RED, dependencias, recursos USE, JVM.
- **MUST NOT** crear un dashboard sin dueño ni enlace a su runbook.

## jvm-observability

- **MUST** exponer las métricas de JVM de Micrometer (`jvm.memory.*`, `jvm.gc.*`, `jvm.threads.*`, `jvm.classes.*`) y las del pool de conexiones (Hikari).
- **MUST** tener un dashboard por servicio con: heap usado tras GC, pausas de GC, hilos vivos/bloqueados, utilización de pools, CPU y throttling del contenedor.
- **MUST** relacionar memoria de la JVM con el `limit` del contenedor: alertar por cercanía de OOMKilled, no solo por heap.
- **MUST** habilitar `-XX:+HeapDumpOnOutOfMemoryError` con ruta a un volumen efímero con espacio; **MUST NOT** subir volcados a sitios sin control de acceso (contienen datos).
- **SHOULD** usar JFR (continuo, de bajo overhead) para diagnóstico bajo demanda en lugar de agentes de profiling permanentes.
- **SHOULD** exponer métricas de executors (`ExecutorServiceMetrics`) y de hilos virtuales o pinning si se usan (comprobar qué eventos JFR).
- **MUST NOT** alertar por uso de heap bruto; alertar por síntoma (latencia, errores) y usar la JVM como diagnóstico.
- **SHOULD** registrar `jvm.info` / versión de JDK como atributo para correlacionar regresiones con upgrades.

## llm-observability

- **MUST** envolver cada llamada a un modelo en un span con atributos de modelo, proveedor, tokens de entrada y salida, motivo de finalización y estado de error, siguiendo las convenciones semánticas de GenAI (estado Development en OpenTelemetry a 2026-11-08, así que los nombres como `gen_ai.request.model` y `gen_ai.usage.input_tokens` pueden cambiar).
- **MUST** exponer métricas: latencia (histograma) incluyendo tiempo hasta el primer token si hay streaming, tokens consumidos, errores por tipo, reintentos y rate limits.
- **MUST** estimar coste por petición a partir de tokens y tarifa configurable; el coste es una métrica, no un cálculo manual.
- **MUST NOT** registrar prompts ni respuestas completos por defecto: pueden contener PII o secretos. Si se capturan para depuración, deben ser opt-in, muestreados, enmascarados y con retención corta.
- **MUST NOT** usar prompt, usuario o ID de conversación como tag de métrica.
- **SHOULD** trazar cada paso de un agente/RAG (recuperación, llamada a herramienta, llamada a modelo) como spans hijos de la petición.
- **SHOULD** medir calidad con evaluaciones (conjunto dorado, comprobaciones automáticas, feedback de usuario) y versionar prompts, para correlacionar regresiones con cambios.
- **SHOULD** fijar timeouts, presupuestos de tokens y alertas de coste y de tasa de error (ver `http-clients-and-timeouts`).

## metrics-micrometer

- **MUST** inyectar `MeterRegistry`; **MUST NOT** usar `Metrics.globalRegistry` salvo en librerías sin Spring.
- **MUST** nombrar en minúsculas con puntos (`orders.created`); Micrometer lo traduce al formato de cada backend.
- **MUST NOT** usar como tag valores no acotados: IDs, emails, URLs con parámetros, mensajes de excepción.
- **MUST** mantener tags de un conjunto cerrado y conocido (estado, canal, tipo de error); documentar el conjunto.
- **MUST** medir latencia con `Timer` (no con gauge ni contador de ms) y habilitar histogramas para SLO en los endpoints críticos.
- **SHOULD** usar `@Timed`/Observation API para handlers, y registrar el meter una vez (campo), no en cada llamada con tags dinámicos.
- **SHOULD** añadir tags comunes (`application`, `region`) con `management.metrics.tags.*`, no a mano.
- **MUST** exponer solo `health` y `prometheus` (y lo estrictamente necesario) en `management.endpoints.web.exposure.include`, en puerto/ruta de gestión no público.
- **MUST NOT** registrar métricas dentro de bucles calientes creando meters nuevos por iteración.

## on-call-and-runbook-links

- **MUST** que cada alerta paginable lleve `runbook_url` a un runbook versionado en el repo del servicio (`docs/runbooks/<alert>.md`) o en la wiki oficial.
- **MUST** que el runbook contenga: qué significa la alerta, impacto, comprobaciones iniciales (con enlaces a dashboard y consultas de logs/trazas), mitigaciones seguras, cuándo escalar y a quién.
- **MUST** que las mitigaciones destructivas (borrar datos, reiniciar bases de datos, rollback de esquema) se describan como texto con advertencia y requieran confirmación humana; **MUST NOT** incluir comandos peligrosos listos para pegar sin contexto.
- **MUST** que cada dashboard enlace a su runbook y a los de sus dependencias, y cada servicio tenga un dueño y un canal de escalado definidos.
- **SHOULD** probar los runbooks en ejercicios (game days) y corregirlos tras cada uso.
- **MUST** hacer postmortem sin culpas de cada incidente que consuma presupuesto de error significativo, con acciones con dueño y fecha.
- **SHOULD** limitar la carga de guardia (páginas por turno) y tratar el exceso como deuda de fiabilidad (ver `alerting-symptom-based`).
- **MUST NOT** guardar credenciales ni datos personales en runbooks; referirse al gestor de secretos.

## otel-fundamentals-and-semconv

- **MUST** definir el `Resource` en cada servicio: `service.name`, `service.version`, `deployment.environment.name` (nombre vigente del atributo: comprobar al fijar la versión) y `service.namespace`.
- **MUST** usar nombres de atributo de las convenciones semánticas (`http.request.method`, `http.response.status_code`, `http.route`, `server.address`) en lugar de nombres propios.
- **MUST** exportar por OTLP al Collector, no directamente a cada backend; el Collector aplica `memory_limiter`, `batch`, redacción y enrutado.
- **MUST NOT** usar identificadores no acotados (userId, orderId, URL completa) como atributo de métrica; sí pueden ir en spans y logs.
- **MUST NOT** poner datos personales, tokens ni cuerpos completos en atributos de span.
- **SHOULD** prefijar atributos propios con el dominio (`acme.order.channel`) para no colisionar con semconv.
- **SHOULD** correlacionar las tres señales por `trace_id`/`span_id` y por los mismos atributos de Resource.
- **SHOULD** versionar la configuración del Collector en el repo del servicio o de plataforma (observabilidad como código).

## otel-java-agent-vs-sdk

- **MUST** elegir UNA vía principal por servicio y documentarla en su README: (a) agente Java, (b) Micrometer Tracing + puente OTel, (c) SDK/starter de OTel.
- **SHOULD** preferir el agente Java por defecto: instrumenta JDBC, HTTP clients, Kafka y servlet sin tocar código, y se actualiza sin recompilar.
- **MUST NOT** combinar agente y puente Micrometer/OTel sobre los mismos spans: produce spans duplicados o trazas partidas.
- **MUST** fijar la versión del agente (no `latest`) y verificar su checksum al construir la imagen.
- **MUST** configurar el agente por variables `OTEL_*` (servicio, endpoint, muestreo), no por código.
- **SHOULD** usar la API de OTel (`io.opentelemetry.api`) o la Observation API de Spring para spans manuales de negocio, nunca el SDK interno.
- **MUST** probar el arranque con y sin agente en CI; el servicio debe funcionar si el Collector no responde.
- **MUST NOT** activar instrumentaciones que no se usan (reduce overhead y superficie).

## slo-sli-error-budgets

- **MUST** definir SLIs como razón de eventos buenos sobre eventos válidos, medidos en el servidor o en el borde más cercano al usuario.
- **MUST** definir al menos: disponibilidad (peticiones no-5xx) y latencia (porcentaje bajo un umbral) por cada API crítica; **SHOULD** añadir frescura/corrección para pipelines de datos.
- **MUST** fijar el SLO como objetivo y ventana (p. ej. 30 días móviles) y derivar el presupuesto de error (`1 - SLO`); el SLO debe ser menor que lo que el diseño soporta (ver `ADR-0007` tier de resiliencia).
- **MUST** versionar SLOs como código (reglas de grabación Prometheus y/o definiciones SLO) junto al servicio, con dueño.
- **MUST** vincular las alertas paginables al consumo del presupuesto (burn rate, ver `alerting-symptom-based`).
- **SHOULD** definir una política de presupuesto agotado acordada con producto: congelar cambios no urgentes, priorizar fiabilidad.
- **MUST NOT** fijar el 100 %; **MUST NOT** copiar SLOs de otro servicio sin medir el comportamiento real.
- **MUST NOT** excluir del SLI las peticiones fallidas "por culpa del cliente" salvo que se definan por código de respuesta explícito.
- **SHOULD** revisar los SLOs trimestralmente con los datos reales.

## structured-logging

- **MUST** emitir logs a stdout en JSON, una línea por evento; el agente de la plataforma los recoge. **MUST NOT** escribir ficheros de log dentro del contenedor.
- **MUST** incluir `timestamp` (UTC, ISO-8601), `level`, `logger`, `message`, `service.name`, `trace_id` y `span_id`.
- **MUST** propagar la correlación vía MDC o integración de OTel/Micrometer, y limpiar el MDC al terminar tareas asíncronas (ver `async-and-context-propagation`).
- **MUST NOT** incluir PII, secretos ni cuerpos completos; aplicar enmascarado en el encoder o en el Collector.
- **MUST NOT** usar etiquetas de Loki de alta cardinalidad (`trace_id`, `user_id`); las etiquetas son pocas (`service`, `namespace`, `level`) y el resto se filtra por contenido.
- **SHOULD** registrar una sola vez cada error, con la excepción como último argumento.
- **SHOULD** usar el soporte nativo de logging estructurado de Spring Boot si la versión lo ofrece (comprobar desde qué versión y formatos), o un encoder JSON explícito.
- **SHOULD** definir un campo `event` estable en eventos de negocio para poder consultarlos y alertar.

## tracing

- **MUST** propagar contexto con W3C Trace Context (`traceparent`); **MUST NOT** inventar cabeceras propias de correlación.
- **MUST** propagar el contexto en hilos propios y `CompletableFuture`/executors (ver `async-and-context-propagation`); con virtual threads, verificar que se mantiene.
- **MUST** propagar el contexto en mensajes Kafka vía cabeceras (instrumentación del cliente o de Spring Kafka con observación activada: comprobar propiedades).
- **MUST** crear spans manuales solo para operaciones de negocio con significado; nombre de baja cardinalidad (`order.reserve-stock`), nunca con IDs en el nombre.
- **MUST** marcar el span como error (estado y excepción) cuando falla; **MUST NOT** marcar error por respuestas 4xx esperadas de cliente.
- **MUST NOT** guardar PII, tokens ni payloads en atributos o eventos de span.
- **SHOULD** usar muestreo por cabecera del padre (`parentbased`) con ratio bajo en producción y 100 % en entornos de prueba; **SHOULD** considerar muestreo por cola en el Collector para conservar errores y trazas lentas.
- **SHOULD** enlazar con `span links` en consumidores por lotes en vez de un padre único.
- **SHOULD** habilitar exemplars o enlaces métrica-traza si el stack lo permite (comprobar al fijar la versión).
