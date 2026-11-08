# Estándares · 06-api-and-integration

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## api-versioning-deprecation

- **MUST** usar versión mayor en la ruta para APIs REST (`/v1/orders`); minor/patch solo en `info.version` del contrato.
- **MUST** preferir evolución compatible dentro de la misma versión mayor; una versión nueva solo para cambios rompientes inevitables.
- **MUST** mantener como máximo dos versiones mayores vivas por API.
- **MUST** anunciar la deprecación con antelación mínima acordada (por defecto 6 meses, comprobar con negocio) y marcar `deprecated: true` en OpenAPI.
- **MUST** emitir cabeceras `Deprecation` (RFC 9745) y `Sunset` (RFC 8594) en respuestas de recursos deprecados, con enlace `Link: rel="deprecation"` a la guía de migración.
- **MUST** medir el uso por versión y consumidor (métrica con etiqueta `api_version`) antes de retirar.
- **MUST NOT** retirar una versión con tráfico de consumidores conocidos sin acuerdo explícito.
- **SHOULD** no versionar por cabecera o parámetro salvo requisito de gateway justificado en ADR.

## asyncapi-event-contracts

- **MUST** documentar cada canal, mensaje y esquema en un documento AsyncAPI versionado junto al servicio productor (`src/main/resources/asyncapi/<service>.yaml`).
- **MUST** usar un envelope común con: `id` (UUID, único por evento), `type`, `source`, `time` (UTC), `specversion`/`schemaVersion` y `correlationId`; se recomienda alinear con CloudEvents.
- **MUST** nombrar eventos en pasado de dominio (`order.placed.v1`) y comandos en imperativo; **MUST NOT** nombrarlos por la tecnología.
- **MUST** definir la clave de partición/orden (p. ej. `orderId`) en el contrato.
- **MUST** publicar el esquema (JSON Schema/Avro/Protobuf) y validarlo en CI con compatibilidad (`schema-registry-and-evolution`, `backward-compatibility-rules`).
- **MUST NOT** incluir datos personales innecesarios ni secretos en el payload (`pii-and-data-classification`).
- **SHOULD** preferir eventos con estado suficiente para el consumidor (event-carried state) frente a "solo id", salvo coste justificado.
- **SHOULD** indicar semántica de entrega esperada y política de reintento/DLQ en la descripción del canal.

## backward-compatibility-rules

- **MUST** tratar como compatible: añadir campo opcional en respuesta, añadir endpoint, añadir valor opcional de petición, añadir RPC o campo Protobuf nuevo (número nuevo).
- **MUST** tratar como rompiente: quitar/renombrar campo o ruta, cambiar tipo o formato, volver obligatorio un campo, estrechar un enum de petición, cambiar semántica, cambiar código de estado de éxito.
- **MUST** exigir a los consumidores tolerar campos desconocidos (tolerant reader): `FAIL_ON_UNKNOWN_PROPERTIES=false` en Jackson (`spring.jackson.deserialization.fail-on-unknown-properties=false`, comprobar al fijar la versión).
- **MUST** ampliar un enum de respuesta solo si el contrato documenta que los clientes deben manejar valores desconocidos.
- **MUST** migrar con expand/contract: añadir lo nuevo, migrar consumidores, retirar lo viejo en una versión posterior (`api-versioning-deprecation`).
- **MUST** ejecutar un diff automático del contrato contra la rama principal en CI y bloquear rompientes sin versión mayor nueva.
- **MUST NOT** reutilizar nombres o números retirados con otro significado.
- **SHOULD** registrar cada excepción rompiente aprobada en un ADR.

## batch-file-sftp-integration

- **MUST** transferir con escritura atómica: subir como `name.csv.part` y renombrar a `name.csv` al terminar; el receptor solo lee ficheros sin sufijo temporal.
- **MUST** acompañar cada fichero de checksum (SHA-256) o fichero de control con nº de registros, y validarlo antes de procesar.
- **MUST** procesar cada fichero de forma idempotente: registrar nombre + checksum en una tabla de ficheros procesados y rechazar duplicados.
- **MUST** usar Spring Batch con `chunk`, estado persistente y reinicio (`JobRepository`); **MUST NOT** cargar el fichero completo en memoria.
- **MUST** definir política de errores por registro (`skip` con límite, a fichero de rechazos) y de fichero (mover a `error/`).
- **MUST** autenticación SFTP por clave, **verificación de host key** (nunca aceptar todas) y credenciales en el gestor de secretos.
- **MUST NOT** registrar contenido de registros con PII; cifrar ficheros sensibles en tránsito (SFTP) y reposo, y aplicar retención/borrado.
- **SHOULD** versionar el layout del fichero y documentarlo como contrato (columnas, codificación UTF-8, separador, formato de fecha ISO-8601).
- **SHOULD** carpetas `inbox/`, `processing/`, `done/`, `error/` y ventana de proceso documentada.

## contract-testing-pact

- **MUST** que el consumidor genere el pact desde un test que ejerce su cliente real contra un mock, describiendo solo lo que realmente usa.
- **MUST** que el proveedor verifique todos los pacts de sus consumidores en CI con estados (`@State`) deterministas.
- **MUST** publicar pacts y resultados en un Pact Broker (OSS) etiquetados con commit y rama, y usar `can-i-deploy` como puerta antes de promover.
- **MUST NOT** usar matchers por valor exacto donde basta el tipo (`like`, regex); **MUST NOT** incluir datos reales ni PII.
- **MUST NOT** probar lógica de negocio del proveedor desde el pact; solo forma y semántica del contrato.
- **SHOULD** usar `pending pacts` y `work in progress pacts` para que un contrato nuevo no rompa la build del proveedor.
- **SHOULD** pact de mensajes para eventos, junto al esquema (`schema-registry-and-evolution`).
- **SHOULD** el proveedor ejecute la verificación con el servicio real levantado en el slice de test (Spring Boot test), con dependencias externas simuladas.

## delivery-semantics

- **MUST** asumir **at-least-once** como base: todo consumidor recibe duplicados.
- **MUST** declarar por integración su garantía (at-most-once, at-least-once, efectivamente-una-vez) en el contrato (AsyncAPI / documento de diseño).
- **MUST** lograr "efectivamente una vez" con idempotencia en el receptor (tabla de eventos procesados con clave única `eventId`), no esperando exactly-once del transporte.
- **MUST** publicar eventos de dominio con el patrón **outbox transaccional** (fila en la misma transacción que el cambio de estado + relay); **MUST NOT** hacer doble escritura BD + broker sin outbox.
- **MUST NOT** depender del orden global; el orden solo se garantiza por clave de partición/grupo de mensajes.
- **MUST** que el consumidor registre el `eventId` y aplique el efecto en la misma transacción local.
- **SHOULD** incluir en cada evento `eventId` (UUID), `occurredAt` y versión del esquema.
- **SHOULD** usar transacciones Kafka (`read_committed`) solo para pipelines Kafka-a-Kafka; no cubren efectos en BD externas.
- **SHOULD** purgar la tabla de eventos procesados con una retención mayor que la ventana máxima de reentrega.

## dlq-retries-poison-messages

- **MUST** distinguir errores transitorios (red, timeout, 503: reintentar) de permanentes (validación, deserialización, regla de negocio: a DLQ sin reintentar).
- **MUST** limitar los reintentos y usar backoff exponencial con jitter; **MUST NOT** reintentar en bucle infinito ni sin espera.
- **MUST** enviar a una DLQ el mensaje que agota reintentos, conservando payload original, clave, cabeceras y motivo (excepción, intentos, topic/partición/offset de origen).
- **MUST** tener alerta sobre la profundidad/tasa de la DLQ y un runbook de reproceso.
- **MUST NOT** perder mensajes en silencio (`catch` que solo registra y confirma).
- **MUST** garantizar que reprocesar desde la DLQ es seguro (consumidor idempotente, ver `delivery-semantics`).
- **SHOULD** usar topics/colas de reintento por etapas solo si el bloqueo de la partición es inaceptable; si no, reintento en proceso con backoff corto.
- **SHOULD** contener PII fuera de los logs de la DLQ; tratar la DLQ con el mismo control de acceso y retención que la fuente.

## graphql

- **MUST** escribir primero el esquema (`.graphqls`, schema-first) y revisarlo como contrato.
- **MUST** resolver relaciones con `@BatchMapping` o DataLoader para evitar N+1 (ver `n-plus-one`).
- **MUST** limitar profundidad y complejidad de consulta y tamaño de página; **MUST NOT** permitir consultas sin cota.
- **MUST** desactivar introspección en entornos expuestos a terceros salvo necesidad documentada.
- **MUST** autorizar en cada resolver/campo sensible (`@PreAuthorize` o equivalente), no solo en el endpoint `/graphql`.
- **MUST** usar paginación por conexiones/cursor para listas (`pagination-filter-sort`).
- **MUST NOT** filtrar excepciones internas en `errors[]`; mapear a errores con `extensions.code` estable.
- **SHOULD** evolucionar con `@deprecated(reason:)` en lugar de versiones; añadir campos nunca rompe, quitarlos sí.
- **SHOULD** usar mutaciones con un único argumento `input` y un payload con errores de negocio tipados.

## grpc-protobuf

- **MUST** nombrar paquetes con versión: `package orders.v1;` y ubicar los `.proto` en un directorio propio (`src/main/proto/orders/v1/`).
- **MUST NOT** reutilizar ni cambiar el número ni el tipo de un campo; al borrar, `reserved` número y nombre.
- **MUST** añadir enums con valor 0 `*_UNSPECIFIED`; **MUST NOT** cambiar semántica de valores existentes.
- **MUST** usar mensajes de request/response propios por RPC (`GetOrderRequest`), nunca tipos primitivos o compartidos entre RPC.
- **MUST** fijar deadline en cada llamada cliente y propagarlo; **MUST NOT** llamadas sin deadline.
- **MUST** devolver errores con códigos `Status` correctos (`NOT_FOUND`, `INVALID_ARGUMENT`, `FAILED_PRECONDITION`...), no `UNKNOWN` ni `INTERNAL` por defecto.
- **MUST** ejecutar `buf lint` y `buf breaking` contra la rama principal en CI.
- **SHOULD** usar `google.protobuf.Timestamp` y wrappers/`optional` para presencia explícita.
- **SHOULD** reintentar solo operaciones idempotentes mediante service config, con backoff.

## idempotency-keys

- **MUST** aceptar la cabecera `Idempotency-Key` (UUID generado por el cliente) en los POST que crean recursos o mueven dinero; ausente = 400 si la operación la exige.
- **MUST** guardar clave + huella (hash) del cuerpo + respuesta en la misma transacción que el efecto, en la base de datos relacional del servicio (sin doble escritura a un segundo almacén).
- **MUST** protegerlo con restricción única `(tenant, key)`; una carrera concurrente devuelve 409 o espera, nunca ejecuta dos veces.
- **MUST** devolver la respuesta original almacenada ante la misma clave y mismo cuerpo; **MUST** responder 422/409 si la clave se reutiliza con cuerpo distinto.
- **MUST** definir TTL (p. ej. 24 h, a confirmar con negocio) y limpieza programada.
- **MUST NOT** derivar la clave en servidor del contenido para operaciones que legítimamente pueden repetirse.
- **SHOULD** aplicar el mismo patrón en consumidores: tabla de `processed_message_id` (ver `delivery-semantics`).
- **SHOULD** alinear la cabecera con el borrador IETF `Idempotency-Key` (`draft-ietf-httpapi-idempotency-key-header-08`, en la cola del RFC Editor el 2026-11-08).

## kafka-producers-consumers

- **MUST** configurar el productor con `acks=all` y `enable.idempotence=true`.
- **MUST** fijar `delivery.timeout.ms` explícito y tratar el fallo del `send` (callback / `CompletableFuture`), nunca ignorarlo.
- **MUST** usar una clave de partición con significado de negocio (p. ej. `orderId`) cuando importe el orden por entidad.
- **MUST** desactivar el auto-commit del consumidor (`enable.auto.commit=false`) y confirmar offsets solo tras procesar con éxito.
- **MUST** hacer el procesamiento idempotente (ver `delivery-semantics`): el consumidor recibirá duplicados.
- **MUST** configurar `ErrorHandlingDeserializer` para que un mensaje corrupto no bloquee la partición.
- **MUST** definir `group.id` explícito por servicio; **MUST NOT** compartirlo entre aplicaciones distintas.
- **MUST NOT** hacer llamadas bloqueantes largas dentro del listener que superen `max.poll.interval.ms`.
- **SHOULD** dimensionar `concurrency` <= nº de particiones del topic.
- **SHOULD** usar el patrón outbox (no doble escritura BD + Kafka) para publicar eventos de dominio.
- **SHOULD** cabeceras estándar: `eventId`, `eventType`, `traceparent`.

## openapi-contract-first

- **MUST** versionar el contrato en el repo del servicio: `src/main/resources/openapi/<service>.yaml` (OpenAPI 3.x), revisado en el mismo PR que el código.
- **MUST** escribir el contrato antes de la implementación y generar interfaces/DTOs desde él (p. ej. `openapi-generator-maven-plugin` con `interfaceOnly`), no al revés.
- **MUST** definir `operationId` únicos, `summary`, respuestas de error (`application/problem+json`) y `examples` en cada operación.
- **MUST** reutilizar esquemas con `$ref` en `components`; **MUST NOT** duplicar esquemas inline.
- **MUST** pasar un linter (Spectral) y un chequeo de ruptura (`backward-compatibility-rules`) en CI.
- **SHOULD** declarar `security` por operación y `servers` sin URLs reales de producción.
- **MUST NOT** generar el contrato desde anotaciones como fuente de verdad (springdoc) salvo para detectar deriva: el contrato escrito manda.
- **SHOULD** validar en test que la respuesta real cumple el contrato (validador de request/response contra el YAML).

## pagination-filter-sort

- **MUST** paginar toda colección; **MUST NOT** devolver listas sin límite.
- **MUST** imponer `size` máximo en servidor (p. ej. 100) y un valor por defecto; rechazar o recortar valores superiores de forma documentada.
- **MUST** usar paginación por cursor (keyset) para datos grandes o que cambian; offset solo para listados pequeños y estables.
- **MUST** hacer la ordenación determinista: añadir un desempate único (`id`) al `ORDER BY`.
- **MUST** validar con lista blanca los campos de `sort` y `filter`; **MUST NOT** concatenarlos en SQL/JPQL.
- **MUST** devolver metadatos: `items`, `nextCursor` (o `page`/`totalElements` si offset) y no exponer cursores interpretables (opacos, firmados o base64 de contenido no sensible).
- **SHOULD** evitar `count(*)` total en tablas grandes; ofrecer `hasMore`.
- **SHOULD** usar sintaxis uniforme: `?size=50&cursor=...&sort=createdAt:desc&status=PAID`.

## rabbitmq-sqs

- **MUST** elegir cola cuando el mensaje es una tarea para un consumidor; Kafka cuando es un hecho que varios lectores reproducen.
- **MUST** acks manuales en RabbitMQ (`acknowledge-mode: manual` o `auto` de Spring con excepciones bien tratadas) y `prefetch` acotado.
- **MUST** colas **quorum** en RabbitMQ para datos que no se pueden perder, con publisher confirms y mensajes `persistent`.
- **MUST** en SQS fijar `VisibilityTimeout` > tiempo máximo de proceso, `ReceiveMessageWaitTimeSeconds` (long polling) y una redrive policy con DLQ (ver `dlq-retries-poison-messages`).
- **MUST** borrar el mensaje SQS solo tras procesar con éxito.
- **MUST** consumidores idempotentes: SQS estándar es at-least-once y sin orden estricto; RabbitMQ reentrega tras desconexión.
- **SHOULD** SQS FIFO solo si se necesita orden/deduplicación; usar `MessageGroupId` con cardinalidad suficiente.
- **SHOULD** cifrado en reposo (SSE) y política de cola con mínimo privilegio en SQS.
- **MUST NOT** enviar payloads grandes por cola; guardar el objeto aparte y enviar la referencia. Tamaño máximo de mensaje en SQS: 1 MiB (1.048.576 bytes; verificado el 2026-11-08); para más, la Extended Client Library guarda el payload en S3 y envía la referencia.

## rate-limiting-quotas

- **MUST** definir límites por identidad de cliente (client id / tenant), no solo por IP, y por clase de operación (lectura vs escritura).
- **MUST** responder 429 con `Retry-After` (segundos) y cuerpo `problem+json` al superar el límite.
- **MUST** distinguir tasa (req/s, ráfaga) de cuota (volumen por día/mes) y documentar ambas en el contrato y en la guía del consumidor.
- **MUST** aplicar el límite de forma compartida entre réplicas (contador en gateway o almacén compartido), no en memoria por instancia.
- **MUST** definir el comportamiento si el almacén del contador falla (fail-open o fail-closed) y registrarlo como decisión.
- **SHOULD** exponer cabeceras informativas de límite restante; el formato `RateLimit-*` es un borrador IETF (`draft-ietf-httpapi-ratelimit-headers-11`, mayo de 2026, camino de estándar; verificado el 2026-11-08), documentar el que se use.
- **SHOULD** hacer que los clientes propios reintenten con backoff exponencial + jitter y respeten `Retry-After`.
- **MUST NOT** devolver 503 ni 403 para un límite de tasa.

## rest-design-guidelines

- **MUST** modelar sustantivos en plural y en minúsculas con guiones: `/orders/{orderId}/lines`; sin verbos en la ruta.
- **MUST** usar los verbos según su semántica (RFC 9110): GET seguro e idempotente, PUT/DELETE idempotentes, POST para crear o acciones no idempotentes, PATCH para cambios parciales.
- **MUST** devolver el código correcto: 201 + `Location` al crear, 204 sin cuerpo, 400 validación, 401/403 authn/authz, 404, 409 conflicto, 422 solo si se documenta, 429 límite.
- **MUST** devolver errores como `application/problem+json` (RFC 9457) con `type`, `title`, `status`, `detail` y un `traceId`.
- **MUST NOT** exponer entidades JPA: usar DTOs (`record`) con propiedades en `camelCase`.
- **MUST NOT** devolver 200 con un cuerpo de error ni filtrar stack traces.
- **SHOULD** usar ids opacos (UUID/ULID), fechas ISO 8601 en UTC y dinero como objeto `{amount, currency}` con decimal en texto.
- **SHOULD** modelar acciones de negocio como sub-recurso (`POST /orders/{id}/cancellation`) antes que verbos.
- **SHOULD** soportar `ETag`/`If-Match` en actualizaciones con riesgo de pisado.

## schema-registry-and-evolution

- **MUST** registrar todo esquema de evento en un registry; **MUST NOT** publicar JSON libre sin esquema en topics compartidos.
- **MUST** fijar la compatibilidad del subject en `BACKWARD_TRANSITIVE` o `FULL_TRANSITIVE` como mínimo para topics con consumidores de terceros.
- **MUST** comprobar compatibilidad en CI antes de fusionar un cambio de esquema.
- **MUST** añadir campos nuevos como opcionales con valor por defecto; **MUST NOT** borrar ni renombrar campos usados, ni cambiar su tipo.
- **MUST NOT** reutilizar un número de campo Protobuf eliminado (usar `reserved`).
- **MUST** desactivar el registro automático de esquemas en producción (`auto.register.schemas=false`); los esquemas se publican desde CI.
- **SHOULD** una estrategia de subject coherente (`TopicNameStrategy` por defecto) y un solo tipo de evento por topic salvo decisión explícita.
- **SHOULD** romper con un topic nuevo versionado (`orders.v2`) cuando el cambio es incompatible, con doble publicación temporal.
- **SHOULD** preferir un registry con licencia OSS (p. ej. Apicurio Registry); Confluent Schema Registry se publica bajo la Confluent Community License, salvo las librerías cliente (Apache 2.0), y no es una licencia de código abierto permisiva (D16; verificado el 2026-11-08).

## sdk-generation

- **MUST** generar el SDK desde el OpenAPI versionado del proveedor; la especificación es la fuente de verdad (ver `openapi-contract-first`).
- **MUST** fijar la versión exacta del generador (p. ej. OpenAPI Generator, licencia Apache-2.0) y su configuración en el repo; **MUST NOT** usar versiones flotantes.
- **MUST NOT** editar a mano el código generado; las personalizaciones van en plantillas, `.openapi-generator-ignore` o envoltorios propios.
- **MUST** publicar el SDK como artefacto separado (módulo Maven / paquete npm) con SemVer alineado al contrato: cambio incompatible = major.
- **MUST** regenerar en CI y fallar si el código generado versionado difiere de la salida (no hay deriva); preferible no versionar el código generado y construirlo en build.
- **MUST** que el generador Java no introduzca Lombok (D27): comprobar opciones y dependencias resultantes.
- **MUST** timeouts, reintentos solo idempotentes y propagación de `traceparent` configurables en el cliente.
- **SHOULD** mantener los tests de contrato (`contract-testing-pact`) contra el SDK generado.
- **SHOULD** registrar credenciales fuera del SDK; el SDK recibe un proveedor de token, no secretos embebidos.
- **SHOULD** documentar en el README del SDK versión del contrato, compatibilidad y política de deprecación.

## soap-legacy-integration

- **MUST** partir del WSDL/XSD del proveedor como contrato (contract-first) y generar clases en build (JAXB / Spring-WS / CXF); **MUST NOT** editarlas a mano ni versionarlas si se generan.
- **MUST** aislar el servicio SOAP tras una **capa anticorrupción** (puerto + adaptador): el dominio nunca ve tipos JAXB.
- **MUST** configurar timeouts de conexión y lectura y un circuit breaker/reintentos solo en operaciones idempotentes.
- **MUST** deshabilitar DTD y entidades externas en todo parser XML (XXE): `disallow-doctype-decl` o `ACCESS_EXTERNAL_DTD=""`.
- **MUST** TLS (mTLS si el proveedor lo exige) y, si se pide WS-Security, usar la librería estándar (Wss4j) con el mismo tratamiento de secretos que otros credenciales.
- **MUST** mapear `SOAP Fault` a excepciones tipadas del puerto y no filtrar su detalle al cliente final.
- **SHOULD** pruebas con respuestas XML grabadas (WireMock) y validación contra el XSD.
- **SHOULD** registrar el envelope solo con campos sensibles enmascarados.
- **SHOULD** documentar la fecha de retirada o plan de sustitución del sistema heredado.

## webhooks

### Receptor
- **MUST** verificar la firma HMAC-SHA256 sobre el **cuerpo crudo** (bytes) antes de parsear, con comparación en tiempo constante (`MessageDigest.isEqual`).
- **MUST** validar un timestamp firmado y rechazar fuera de una ventana (p. ej. 5 minutos) contra replay.
- **MUST** responder 2xx rápido y procesar en asíncrono; **MUST** deduplicar por `eventId` (ver `delivery-semantics`).
- **MUST NOT** confiar en la IP origen como único control ni registrar el secreto o el cuerpo con PII.
### Emisor
- **MUST** firmar cada entrega, incluir `eventId` y timestamp, y reintentar con backoff exponencial hasta un máximo, luego marcar fallida.
- **MUST** proteger contra SSRF: solo HTTPS, resolver DNS y rechazar IPs privadas/loopback/link-local (incl. metadatos de nube), sin seguir redirecciones ciegamente.
- **MUST** timeouts cortos de conexión y lectura.
- **SHOULD** permitir rotación de secretos con dos secretos válidos a la vez.
- **SHOULD** exponer log de entregas y reenvío manual al cliente.
