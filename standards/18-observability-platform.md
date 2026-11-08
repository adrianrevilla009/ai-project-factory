# Estándares · 18-observability-platform

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## alert-routing-and-oncall

- **MUST** que toda alerta que despierte a una persona sea accionable, urgente y con `runbook_url` en anotaciones; el resto va a ticket o dashboard.
- **MUST** usar dos niveles de severidad como mínimo (`critical` page, `warning` ticket) y rutear por `matchers` sobre `severity` y `team`.
- **MUST** definir `group_by` (p. ej. `[cluster, alertname, namespace]`), `group_wait`, `group_interval` y `repeat_interval` explícitos.
- **MUST** `inhibit_rules` para suprimir síntomas cuando existe la causa (p. ej. `warning` si hay `critical` con el mismo `instance`/`service`).
- **MUST** alertar sobre síntomas (burn rate de SLO, errores, latencia) y no sobre causas (CPU alta) salvo capacidad.
- **MUST** una alerta "watchdog" siempre activa hacia un monitor externo que avise si la cadena de alertado cae.
- **SHOULD** un receiver por equipo; secretos de webhooks fuera del repo (`*_file` o variables).
- **SHOULD** silencios con caducidad y autor; revisión mensual de alertas ruidosas.
- **MUST NOT** usar `repeat_interval` muy corto como sustituto de escalado.
- La herramienta de guardia (PagerDuty u otra) es de pago: por defecto, receiver webhook/Slack/email y la herramienta como adaptador opcional (D16).

## cardinality-and-cost-governance

- **MUST** que ninguna etiqueta de métrica tome valores no acotados (ID de usuario, pedido, email, URL con parámetros, traceId).
- **MUST** usar la plantilla de ruta (`/orders/{id}`) y no la URL cruda como etiqueta `uri`.
- **MUST** presupuesto de series activas por servicio y tenant; superarlo bloquea el despliegue o dispara alerta.
- **MUST** límites duros en el scrape: `sample_limit`, `label_limit` y `label_value_length_limit` por job (confirmar nombres: comprobar al fijar la versión).
- **MUST** eliminar en origen lo no usado con `metric_relabel_configs` (`action: drop`) o en el Collector, antes de almacenar.
- **MUST** vigilar `prometheus_tsdb_head_series` y las top-N métricas por series con un dashboard y alerta de crecimiento.
- **SHOULD** buckets de histograma justificados; cada bucket multiplica series por las demás etiquetas.
- **SHOULD** muestreo de trazas (por cola, errores y latencia siempre) y niveles de log en producción `INFO`.
- **SHOULD** atribuir coste por tenant/equipo (showback) y revisarlo mensualmente.
- **MUST NOT** convertir en etiqueta lo que es un atributo de span o un campo de log.

## collector-pipelines

- **MUST** declarar `memory_limiter` como primer processor y `batch` como último en cada pipeline; el orden de `processors` es el orden de ejecución.
- **MUST** separar dos capas: agente (DaemonSet, receivers OTLP locales, enriquecimiento k8s) y gateway (Deployment, muestreo, enrutado por tenant, exportación).
- **MUST** definir un pipeline por señal (`traces`, `metrics`, `logs`) y variantes con `type/name` (`traces/errors`) en lugar de un único pipeline con condiciones.
- **MUST** habilitar la extensión `health_check` y usarla en liveness/readiness.
- **MUST NOT** hacer tail sampling en el agente: necesita todos los spans de una traza en la misma réplica; usar gateway con balanceo por `traceID` (comprobar exporter `loadbalancing` en la distribución contrib usada).
- **MUST NOT** exportar sin cola/reintentos configurados ni sin límite de memoria (el Collector es un punto único de pérdida de telemetría).
- **SHOULD** usar la distribución contrib solo si hacen falta componentes contrib; mejor construir una distribución mínima con `ocb` (OpenTelemetry Collector Builder) fijando versiones.
- **SHOULD** exportar a Tempo y Loki por OTLP y a Prometheus por remote write o scrape del endpoint del Collector.
- **MUST NOT** poner tokens o contraseñas en el YAML: usar variables de entorno `${env:NAME}` alimentadas desde Secret.

## dashboards-and-slos-as-code

- **MUST** versionar dashboards en Git (JSON exportado o generado con Grafonnet/Jsonnet u otra librería) y provisionarlos por fichero (`providers` de dashboards) o por ConfigMap; la edición en la UI no es fuente de verdad.
- **MUST** `allowUiUpdates: false` en el provider de producción para que la UI no diverja de Git.
- **MUST** definir cada SLO en una spec declarativa (objetivo, ventana, SLI en PromQL) de la que se generan reglas de grabación y alertas de burn rate multiventana; no escribir esas reglas a mano.
- **MUST** `uid` estable y `title` único por dashboard; datasources por `uid`, no por nombre.
- **MUST** que todo dashboard de servicio use variables (`namespace`, `service`) y muestre los 4 golden signals (latencia, tráfico, errores, saturación) más el SLO.
- **SHOULD** el SLO vive en el repo del servicio; los dashboards de plataforma, en el repo de plataforma.
- **SHOULD** el generador de SLOs sea de código abierto (p. ej. Sloth o Pyrra; elegir por ADR, comprobar formato de spec vigente).
- **MUST NOT** SLOs al 100% ni sin ventana; el objetivo debe tener error budget con política asociada.

## logs-and-traces-stores

- **MUST** usar almacenamiento de objetos (S3 en AWS, MinIO en local) para chunks y bloques; el disco local solo para WAL/caché.
- **MUST** habilitar retención de Loki en el compactor: `compactor.retention_enabled: true`, `compactor.delete_request_store` y `limits_config.retention_period`; sin `retention_enabled` el compactor solo compacta.
- **MUST** usar periodo de índice de 24h (requisito de la retención) y esquema TSDB (versión de `schema` por confirmar: comprobar al fijar la versión).
- **MUST** mantener pocas etiquetas de Loki, de baja cardinalidad (`namespace`, `app`, `level`); IDs de usuario, de traza o de petición van en el cuerpo del log, no como etiqueta.
- **MUST** fijar retención de bloques de trazas en Tempo (compactor) con un valor menor que el de logs.
- **SHOULD** correlacionar logs y trazas con `trace_id` en el cuerpo (JSON) y derived fields en Grafana.
- **SHOULD** retención diferenciada por flujo (`retention_stream`) para logs de auditoría frente a debug.
- **MUST NOT** guardar PII ni secretos en logs (ver `logging-rules`).

## metrics-store-ha-retention

- **MUST** fijar la retención de forma explícita: `--storage.tsdb.retention.time` y `--storage.tsdb.retention.size` (sin ninguno, el defecto es 15d).
- **MUST** poner `retention.size` por debajo de la capacidad del volumen (margen para WAL y compactación) y alertar al 80% de uso del PVC.
- **MUST** ejecutar HA como réplicas independientes que scrapean lo mismo, con `external_labels` distintos por réplica (`replica: a|b`); Prometheus no replica datos entre instancias.
- **MUST** que Alertmanager se despliegue en clúster (mínimo 3 réplicas) y que cada réplica de Prometheus envíe a todas.
- **MUST NOT** tratar el disco local como almacén histórico: más allá de la retención local, usar `remote_write` a un backend de largo plazo.
- **SHOULD** elegir el backend de largo plazo por ADR (candidatos con licencia abierta; comprobar licencia antes: comprobar al fijar la versión), sin licencias de pago por defecto (D16).
- **SHOULD** deduplicar en consulta por el label `replica` y no mezclar réplicas en dashboards.
- **MUST NOT** usar NFS para el TSDB local.

## multi-tenant-observability

- **MUST** definir el tenant como unidad de aislamiento y de límites (ingestión, retención, consultas), mapeado a equipo o entorno, no a servicio.
- **MUST** que el tenant lo inyecte el Collector gateway (cabecera `X-Scope-OrgID` en Loki/Tempo), nunca la aplicación ni el navegador.
- **MUST** habilitar multi-tenencia explícitamente (Loki `auth_enabled: true`; Tempo `multitenancy_enabled: true`; confirmar claves: comprobar al fijar la versión) y poner un proxy de autenticación delante que fije la cabecera según la identidad (Keycloak/OIDC, D-identidad).
- **MUST** un datasource de Grafana por tenant, con la cabecera fija en el datasource y permisos de carpeta/datasource por equipo.
- **MUST** límites por tenant (`limits_config`/overrides): tasa de ingestión, streams máximos, retención.
- **MUST NOT** compartir un tenant "común" para datos de distintos niveles de confidencialidad.
- **SHOULD** mantener tenants de producción y no producción separados.
- **SHOULD** en Prometheus aislar por instancia o por label `tenant` impuesto en remote write (Prometheus no tiene tenancy nativa).

## observability-of-the-platform-itself

- **MUST** una alerta "watchdog" siempre disparando hacia un servicio externo (dead man's switch) que avise cuando deje de llegar.
- **MUST** que el sistema que vigila no sea solo vigilado por sí mismo: al menos una comprobación externa (sonda blackbox desde otro dominio de fallo) a Grafana y a la entrada de alertas.
- **MUST** alertar sobre: pérdida de scrape (`up == 0`), Collector con `refused`/`dropped` en exporters y cola llena, ingesters de Loki/Tempo con errores de escritura, WAL de Prometheus, disco del TSDB y fallos de notificación de Alertmanager.
- **MUST** exponer métricas propias del Collector (telemetría interna) y recogerlas con Prometheus.
- **MUST** SLOs propios de la plataforma (frescura de datos: retraso de ingestión de logs/trazas, disponibilidad de consulta) como cualquier servicio.
- **SHOULD** tests de extremo a extremo sintéticos: emitir un log y una traza de prueba y comprobar que aparecen en Loki/Tempo en N minutos.
- **SHOULD** probar el camino de alerta regularmente (alerta de prueba mensual a cada receiver).
- **MUST NOT** enviar los logs de Loki a Loki sin bucle de protección (no etiquetar su propio ruido con el mismo pipeline sin límite).
- **MUST NOT** dar por válido un dashboard vacío: "sin datos" debe ser un estado alertable.

## status-page-and-comms

- **MUST** alojar la página de estado fuera de la infraestructura que monitoriza (otro clúster/cuenta/proveedor), para que siga disponible en un fallo de la plataforma.
- **MUST** definir componentes visibles al usuario (no microservicios internos) y estados: operativo, degradado, interrupción parcial, interrupción mayor, mantenimiento.
- **MUST** asignar un rol de comunicaciones por incidente, distinto del comandante técnico.
- **MUST** publicar una primera actualización en un plazo acordado por tier (p. ej. 15 min para tier 1; el plazo lo fija `tier-model-and-rpo-rto`) y actualizaciones periódicas aunque sean "sin novedades".
- **MUST** usar lenguaje de impacto al usuario, sin jerga interna, sin culpar a terceros y sin prometer hora de resolución no confirmada.
- **SHOULD** usar una herramienta de código abierto autoalojable (p. ej. Cachet, Uptime Kuma o una página estática; elegir por ADR, comprobar estado de mantenimiento) en lugar de SaaS de pago por defecto (D16).
- **SHOULD** automatizar solo el borrador desde alertas `critical`; la publicación la aprueba una persona.
- **MUST NOT** publicar datos personales, nombres de clientes ni detalles de vulnerabilidades.
- **MUST NOT** reutilizar la misma plantilla para incidentes de seguridad: pasan por el proceso de seguridad y legal (normativa de notificación: borrador por confirmar con fuente oficial).

## tempo-and-service-graphs

- **MUST** habilitar el metrics-generator con los procesadores necesarios (`service-graphs`, `span-metrics`) y un `remote_write` a Prometheus; sin remote write las métricas generadas no se guardan (comprobar claves exactas de overrides en la versión desplegada).
- **MUST** que los spans lleven `service.name` consistente y atributos de peer/mensajería correctos; sin ellos el grafo de servicios queda incompleto o con nodos "desconocidos".
- **MUST** limitar las dimensiones de `span-metrics` a un conjunto acotado (p. ej. `http.method`, `http.route`); no usar atributos de alta cardinalidad (ver `cardinality-and-cost-governance`).
- **MUST** propagar el contexto W3C `traceparent` entre servicios, colas incluidas (cabeceras Kafka).
- **SHOULD** derivar RED (tasa, errores, duración) de span metrics para servicios sin métricas propias, pero preferir las métricas nativas de la aplicación para los SLOs.
- **SHOULD** exemplars en histogramas y datasource Grafana con "trace to logs" y "trace to metrics" configurados.
- **SHOULD** muestreo decidido en el gateway: el metrics-generator debe recibir spans antes de descartarlos si se quieren métricas sin sesgo (comprobar orden recomendado).
- **MUST NOT** usar el service graph como fuente de verdad de arquitectura: es observado, no declarado.
