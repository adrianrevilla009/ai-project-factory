# Estándares · 26-enterprise-capabilities

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## api-productization-and-developer-portal

- **MUST** tratar la API como producto: propietario, ciclo de vida (preview, GA, deprecated, sunset), changelog público y política de versionado y deprecación (`api-versioning-deprecation`).
- **MUST** generar la documentación del portal desde el OpenAPI versionado en el repo; sin docs escritas a mano que diverjan.
- **MUST** ofrecer un sandbox aislado con datos ficticios y credenciales de prueba separadas de producción; sin acceso a datos reales.
- **MUST** autenticar a terceros con OAuth2 client credentials (o claves API para casos simples); las claves se guardan solo como hash, se muestran una vez y se pueden rotar y revocar.
- **MUST** asociar cada credencial a una aplicación, un tenant y un plan con cuotas y límites de tasa (`rate-limiting-quotas`); responder 429 con `Retry-After`.
- **MUST** usar scopes mínimos por aplicación y registrar el consentimiento del propietario.
- **MUST** devolver errores homogéneos (`ProblemDetail`, `code` estable) y un identificador de petición (`X-Request-Id`) para soporte.
- **MUST** pasar el contract gate (diff de OpenAPI) en CI antes de publicar; un cambio incompatible exige versión nueva (`contract-gate`).
- **MUST** medir uso por aplicación/plan (volumen, errores, latencia) sin etiquetas de alta cardinalidad en métricas; el detalle va a logs.
- **SHOULD** publicar colección de ejemplos y guía de inicio rápido que se ejecuten en CI contra el sandbox.
- **SHOULD** generar SDKs desde OpenAPI solo si hay capacidad de mantenerlos; marcar su versión soportada.
- **SHOULD** soportar webhooks firmados con reintentos y panel de entregas (`webhooks`).
- **MUST NOT** exponer endpoints internos o de admin en el mismo gateway/spec público.
- **MUST NOT** cambiar o eliminar campos sin el periodo de deprecación anunciado (plazo por decisión de producto/contrato).

## audit-trail-and-activity-log

- **MUST** registrar por evento: `occurredAt` (UTC), actor (id de usuario o servicio), `tenantId`, acción (código estable), tipo e id del recurso, resultado, `correlationId`.
- **MUST** escribir el evento de auditoría en la misma transacción que el cambio (o vía outbox); un cambio sin rastro no debe existir.
- **MUST** hacer la tabla append-only: sin `UPDATE`/`DELETE` para el rol de la aplicación.
- **MUST** guardar el delta de campos (`before`/`after`) solo de campos permitidos; los datos personales y secretos se omiten o se enmascaran.
- **MUST NOT** registrar contraseñas, tokens ni datos de tarjeta en el payload de auditoría.
- **MUST** auditar también lecturas sensibles, exportaciones y accesos denegados.
- **SHOULD** definir retención por tipo de evento; la retención legal es un borrador por confirmar con asesoría.
- **SHOULD** exponer consulta paginada por keyset con filtros por actor, recurso y rango, restringida por permiso y tenant.
- **SHOULD** separar el historial de usuario (legible, traducido) de la auditoría técnica (códigos estables).
- **MUST NOT** depender de la auditoría para lógica de negocio; si el flujo la necesita, es un modelo de dominio.

## back-office-admin-console

- **MUST** servir la consola como aplicación y API separadas del frontend público (otro host, otro cliente OIDC en Keycloak, otro conjunto de roles). Nunca un flag `isAdmin` dentro de la app pública.
- **MUST** autorizar en el servidor cada endpoint `/admin/**` con permisos granulares (`customer:read`, `refund:approve`), no solo con un rol grueso `ADMIN`.
- **MUST** exigir MFA y sesiones cortas para los usuarios de back-office.
- **MUST** registrar cada acción de escritura en el audit trail (quién, qué, sobre quién, motivo, antes/después) con motivo obligatorio en texto libre o código.
- **MUST** aplicar cuatro ojos (solicitante != aprobador) a acciones sensibles: reembolsos sobre umbral, cambio de datos bancarios, borrado, cambio de rol.
- **MUST** limitar y registrar la impersonación: tiempo máximo, banner visible, sin acceso a credenciales ni a cambio de contraseña/MFA, token marcado con `act` (claim de actor) para que el audit distinga al agente del usuario.
- **MUST** enmascarar por defecto datos personales y sensibles (IBAN, documento) y exigir "revelar" como acción auditada.
- **SHOULD** que las acciones masivas sean asíncronas, con previsualización (dry-run), límite de filas y registro de resultado por fila.
- **MUST NOT** exponer entidades JPA directamente; usar DTO específicos de admin.
- **MUST NOT** reutilizar tokens del frontend público para llamar a la API de admin.

## consent-and-dsar-management

- **MUST** guardar cada consentimiento como evento inmutable: sujeto, finalidad, versión del texto, valor (otorgado/retirado), marca temporal, canal y prueba (IP/UA solo si la finalidad lo justifica).
- **MUST** modelar el consentimiento por finalidad, nunca un único "acepto todo" ni casillas premarcadas.
- **MUST** hacer la retirada tan fácil como el otorgamiento y propagarla a los servicios consumidores por evento (outbox).
- **MUST** modelar el DSAR como un caso con máquina de estados (`RECEIVED`, `IDENTITY_VERIFIED`, `IN_PROGRESS`, `COMPLETED`, `REJECTED`), fecha límite calculada y alerta previa al vencimiento (plazo base de un mes según el art. 12; comprobar prórrogas).
- **MUST** verificar la identidad del solicitante antes de entregar datos.
- **MUST** mantener un inventario de dónde vive cada dato personal (ver `pii-and-data-classification`); sin inventario no hay DSAR fiable.
- **MUST** responder el acceso/portabilidad en formato estructurado (JSON/CSV) y entregarlo por canal seguro con enlace caducable.
- **MUST** ejecutar la supresión por orquestación a todos los sistemas, con excepciones (obligación legal, litigio) registradas y justificadas; en eventos inmutables usar crypto-shredding (`gdpr-and-immutable-events`).
- **MUST NOT** guardar en el log de DSAR los datos entregados; solo metadatos y hash de la entrega.
- **SHOULD** exponer métricas: casos abiertos, edad máxima, casos próximos a vencer.

## document-and-report-generation

- **MUST** generar de forma asíncrona cualquier informe que pueda superar unos segundos: `POST /reports` devuelve `202` con `reportId`; el cliente consulta estado y descarga.
- **MUST** hacer streaming (no cargar el resultado completo en memoria): cursor/`Stream` hacia el escritor, tamaño de página acotado.
- **MUST** guardar el artefacto en almacenamiento de objetos con TTL y descargarlo por URL firmada de corta vida o endpoint autenticado.
- **MUST** autorizar la descarga contra el propietario/tenant del informe, no solo por conocer el id.
- **MUST** separar plantilla de datos; plantillas versionadas en el repo (HTML→PDF, XLSX).
- **MUST NOT** construir HTML de plantilla concatenando entrada del usuario (XSS/SSRF en conversores HTML→PDF); escapar y bloquear recursos remotos.
- **MUST NOT** incluir más campos personales de los necesarios; marcar el informe con clasificación de datos.
- **SHOULD** neutralizar fórmulas en CSV/Excel (prefijos `=`, `+`, `-`, `@`) para evitar CSV injection.
- **SHOULD** elegir librerías con licencia compatible con D16; licencias de iText/JasperReports/otras: comprobar al fijar la versión.

## i18n-and-localization

- **MUST** resolver el locale por petición (cabecera `Accept-Language` o preferencia del usuario) con un `LocaleResolver` único y un locale por defecto explícito.
- **MUST** devolver errores de API con un `code` estable y legible por máquina; el texto traducido es complementario (`ProblemDetail` con `code`), nunca el contrato.
- **MUST** externalizar mensajes en `messages_<locale>.properties` (`MessageSource`), sin cadenas de usuario concatenadas en código; usar placeholders con `MessageFormat`/ICU y plurales.
- **MUST** almacenar instantes en UTC (`Instant`/`timestamptz`) y convertir a la zona del usuario solo al presentar; guardar el `ZoneId` del usuario, no un offset.
- **MUST** guardar importes como cantidad decimal más código ISO 4217 de moneda; formatear según locale al presentar.
- **MUST** usar `Locale.ROOT` o `Locale.ENGLISH` en operaciones técnicas (`toLowerCase`, `String.format` de identificadores) para evitar el fallo del turco.
- **MUST** usar UTF-8 en todo (BD, ficheros, HTTP, `spring.messages.encoding`).
- **SHOULD** modelar contenido traducible como tabla hija `<entity>_translation(entity_id, locale, ...)` con fallback documentado (`es-MX` -> `es` -> default).
- **SHOULD** usar BCP 47 (`es-ES`) como formato de locale en API y BD.
- **MUST NOT** ordenar ni comparar texto de usuario con `compareTo` cuando importa el idioma; usar `Collator`.
- **MUST NOT** asumir que el nombre tiene "nombre + apellido" ni validar teléfonos/direcciones con una regex de un solo país.

## identity-and-customer-management

- **MUST** delegar autenticación y almacén de credenciales en Keycloak; el servicio de negocio NUNCA guarda contraseñas ni hashes.
- **MUST** separar identidad (Keycloak: `sub`, credenciales, MFA) de cliente de negocio (tabla `customer` propia) enlazados por `sub` inmutable, no por email.
- **MUST** crear el registro `customer` de forma idempotente en el primer login o por evento, con clave única sobre `identity_subject`.
- **MUST** tratar el email como atributo mutable y verificado, nunca como clave primaria.
- **SHOULD** usar la Admin REST API de Keycloak solo desde un servicio de backend con cliente de servicio de mínimo privilegio.
- **SHOULD** modelar roles gruesos en Keycloak y permisos de dominio en el servicio.
- **MUST NOT** duplicar en la BD de negocio datos de credenciales ni sincronizar contraseñas.
- **MUST NOT** confiar en claims editables por el usuario (ej. atributos de perfil sin protección) para autorizar.

## import-export-and-bulk-data

- **MUST** procesar importaciones de forma asíncrona: subir fichero a almacenamiento, crear `import_job` con estado (`PENDING/RUNNING/DONE/FAILED`) y procesar por chunks.
- **MUST** validar tipo real, tamaño máximo y número máximo de filas antes de procesar; rechazar lo que exceda.
- **MUST** cargar primero a una tabla de staging, validar y luego aplicar; informe de errores por fila (nº de fila, campo, motivo) descargable.
- **MUST** hacer la importación idempotente: clave natural o `import_job_id + row_number` con restricción única; reintentar un job no duplica.
- **MUST** definir si la política es todo-o-nada o parcial con errores, y documentarla al usuario.
- **MUST NOT** interpretar entrada del usuario como fórmula, ruta o SQL; parámetros enlazados siempre; parsers XML sin entidades externas.
- **MUST NOT** cargar el fichero completo en memoria; lectura en streaming.
- **SHOULD** autorizar por tenant y registrar en auditoría quién importó qué (`audit-trail-and-activity-log`).
- **SHOULD** usar inserciones en lote (`batch size` acotado) y deshabilitar `open-in-view`.

## integrations-erp-crm

- **MUST** aislar el sistema externo tras una anti-corruption layer: un puerto propio (`ErpGateway`) y un adaptador por producto; el modelo del ERP no entra en el dominio (`anti-corruption-layer`).
- **MUST** definir la fuente de verdad por entidad y campo (quién manda: ERP o nosotros) y documentarlo; sin ello habrá conflictos de escritura.
- **MUST** guardar un mapa de identificadores `internal_id <-> external_id` por sistema y entidad.
- **MUST** hacer las llamadas salientes idempotentes (clave de idempotencia o upsert por `external_id`) y reintentables con backoff y jitter.
- **MUST** emitir los cambios a sincronizar vía outbox, no llamando al ERP dentro de la transacción de BD (`outbox-and-cdc`).
- **MUST** configurar timeouts, circuit breaker y bulkhead por integración; el ERP caído no debe tirar la aplicación.
- **MUST** respetar los límites del proveedor (cuotas, lotes) con un limitador propio; los valores concretos se leen de su documentación oficial (comprobar por proveedor).
- **MUST** reconciliar periódicamente (job de conciliación con informe de diferencias) y enviar fallos definitivos a una cola de revisión manual (DLQ).
- **MUST** guardar credenciales de la integración en el gestor de secretos, con OAuth2 client credentials cuando el proveedor lo ofrezca.
- **SHOULD** preferir webhooks/eventos del proveedor más sondeo incremental con marca de agua (`updated_since`) frente a cargas completas.
- **SHOULD** validar la entrada del externo como no confiable (esquema, tamaños, enums desconocidos tolerados).
- **MUST NOT** hacer doble escritura síncrona a nuestro sistema y al ERP sin mecanismo de reconciliación.
- **MUST NOT** registrar payloads con datos personales completos en logs.

## multi-tenancy-saas-features

- **MUST** propagar `tenantId` desde el token validado (claim) hasta el acceso a datos mediante un contexto único; nunca desde un parámetro o cabecera del cliente.
- **MUST** modelar el tenant con estado explícito: `PROVISIONING`, `ACTIVE`, `SUSPENDED`, `OFFBOARDING`, `DELETED`; cada transición es idempotente y auditada.
- **MUST** hacer el onboarding como proceso reanudable (saga/workflow) con pasos idempotentes: crear tenant, esquema/filas, realm u organización en Keycloak, admin inicial, valores por defecto.
- **MUST** centralizar planes y límites como "entitlements" (`feature -> limit`) consultados por una sola API interna; no comparar `plan == "PRO"` por el código.
- **MUST** aplicar cuotas por tenant (peticiones, almacenamiento, usuarios) y devolver 429/402 con `code` claro (ver `rate-limiting-quotas`).
- **MUST** guardar configuración por tenant con esquema validado y valores por defecto de plataforma; los cambios se auditan.
- **MUST** incluir `tenant_id` en claves de caché, claves de objetos, nombres de colas/temas y etiquetas de logs/trazas (no en etiquetas de métricas de alta cardinalidad).
- **MUST** tener test de aislamiento: un tenant A nunca lee ni escribe datos de B, incluyendo caché y búsquedas.
- **MUST** definir offboarding: exportación de datos, periodo de gracia, borrado verificable y su evidencia (ligado a retención y legal, por confirmar).
- **SHOULD** limitar el "vecino ruidoso" con límites por tenant en pools, colas y jobs.
- **MUST NOT** hacer lógica `if (tenant == "acme")`; usar configuración o entitlements.
- **MUST NOT** compartir secretos o claves de cifrado entre tenants cuando el contrato exija aislamiento.

## notifications

- **MUST** desacoplar el origen del envío: el caso de uso emite un evento (outbox, ver `outbox-and-cdc`) y un consumidor `notification-service` envía.
- **MUST** garantizar idempotencia con `notification_key` (evento + destinatario + canal) y restricción única; reintentos no duplican mensajes.
- **MUST** respetar preferencias y consentimiento por canal y propósito (`consent-and-dsar-management`); las transaccionales se distinguen de las de marketing.
- **MUST** reintentar con backoff y DLQ (`dlq-retries-poison-messages`); fallo del proveedor no bloquea la transacción de negocio.
- **MUST** usar plantillas versionadas con i18n (`i18n-and-localization`); sin concatenar texto en código.
- **MUST NOT** registrar en logs el cuerpo, teléfono o email completos (PII).
- **MUST NOT** incluir secretos o tokens de larga vida en enlaces; usar tokens de un solo uso con caducidad.
- **SHOULD** abstraer proveedores tras `NotificationChannelPort` (SMTP local con MailHog/Mailpit en dev; el proveedor real de AWS, p. ej. SES, no se emula localmente y queda comprobar al fijar la versión).

## payments-and-billing

- **MUST** representar dinero como `BigDecimal` o unidades menores (`long`) junto a un código de moneda ISO 4217; nunca `double`/`float`.
- **MUST** enviar una clave de idempotencia en cada operación de cobro/reembolso y persistirla con el pedido.
- **MUST** tratar el webhook del PSP como fuente de verdad del estado del pago; la redirección del navegador solo informa.
- **MUST** verificar la firma del webhook sobre el cuerpo crudo, con comparación en tiempo constante, y rechazar marcas de tiempo antiguas.
- **MUST** deduplicar webhooks por `event.id` (los PSP reintentan y entregan desordenado) y procesarlos de forma idempotente.
- **MUST** modelar el pago como máquina de estados explícita (`PENDING -> AUTHORIZED -> CAPTURED -> REFUNDED/FAILED`) con transiciones validadas.
- **MUST NOT** almacenar PAN, CVV ni datos de tarjeta; usar tokenización/hosted fields del PSP para quedar fuera del alcance PCI en lo posible (comprobar alcance PCI DSS con la fuente oficial).
- **MUST NOT** hacer dual-write entre la BD y el PSP sin outbox o reconciliación (ver `outbox-and-cdc`).
- **SHOULD** ejecutar una conciliación periódica (job) entre registros propios y el informe del PSP.
- **SHOULD** emitir facturas como documentos inmutables numerados; las correcciones son notas de abono, no ediciones.
- **SHOULD** usar el sandbox del PSP en local; no reproducir el PSP real en local.

## rules-engines

- **MUST** empezar por código (patrón Strategy / specification) y justificar por escrito el salto a un motor.
- **MUST** comprobar licencia del motor elegido (D16). Drools/KIE y DMN de Camunda/Flowable: licencia y versión comprobar en documentación oficial.
- **MUST** aislar el motor tras un puerto `PricingRulesPort`; entrada y salida son DTOs inmutables.
- **MUST** versionar reglas junto al código y probarlas con casos tabulares (given/expected).
- **MUST** registrar qué versión de reglas decidió cada resultado (trazabilidad, ver `audit-trail-and-activity-log`).
- **MUST NOT** permitir que reglas editadas en caliente lleguen a producción sin revisión y pruebas.
- **MUST NOT** dar acceso a servicios/BD al motor desde las reglas (efectos laterales).
- **SHOULD** preferir tablas de decisión (DMN) cuando negocio las mantiene.

## scheduling-and-batch-jobs

- **MUST** asegurar ejecución única entre réplicas: bloqueo distribuido (ShedLock con `@SchedulerLock`) o CronJob de Kubernetes con `concurrencyPolicy: Forbid`.
- **MUST** fijar `lockAtMostFor` mayor que la duración esperada y, si hay desfase de relojes, `lockAtLeastFor` (semántica en https://github.com/lukas-krecan/ShedLock, 2026-11-07).
- **MUST** diseñar cada ejecución idempotente y reanudable (marca de progreso, no "todo o nada" sin reintento).
- **MUST** usar chunking con commit interval acotado en Spring Batch; configurar skip/retry por excepción explícita (https://docs.spring.io/spring-batch/reference/step/chunk-oriented-processing.html, 2026-11-07).
- **MUST** exponer métricas de job (duración, filas, fallos) y alertar si no se ejecuta.
- **MUST NOT** usar `@Scheduled` sin bloqueo en servicios replicados.
- **MUST NOT** ejecutar trabajo pesado en el hilo del scheduler por defecto; usar un executor acotado.
- **SHOULD** externalizar el cron a configuración y fijar zona horaria explícita (`zone = "UTC"`).
- **SHOULD** elegir CronJob de Kubernetes para jobs largos aislados y ShedLock para tareas cortas dentro del servicio.

## search-and-discovery

- **MUST** empezar por PostgreSQL (índices, `tsvector`/GIN, `pg_trgm`) si el volumen y los requisitos lo permiten; justificar en ADR el paso a un motor de búsqueda dedicado.
- **MUST** tratar el índice de búsqueda como **vista derivada y reconstruible**: la fuente de verdad es la BD transaccional. Sin doble escritura síncrona Postgres+índice (4.5); alimentar vía outbox/CDC (`outbox-and-cdc`).
- **MUST** poder reindexar completo sin downtime (alias + índice versionado).
- **MUST** aplicar autorización/tenant como filtro obligatorio en cada consulta al índice.
- **MUST** paginar con límite máximo; `search_after`/keyset en vez de offset profundo.
- **MUST NOT** exponer el motor de búsqueda directamente al navegador.
- **MUST NOT** indexar campos sensibles que no se vayan a buscar.
- **SHOULD** preferir OpenSearch (código abierto, Apache 2.0 según su repositorio: licencia comprobar al fijar la versión) sobre soluciones con licencia restrictiva (D16). Preparado para AWS (Amazon OpenSearch Service), no verificado en real; local con contenedor OpenSearch, sin reproducir dimensionado, multi-AZ ni cifrado del servicio gestionado.

## workflow-bpm

- **MUST** decidir el motor por licencia antes de adoptarlo (D16, sin licencias de pago por defecto). Camunda 8 self-managed usa licencia propietaria y exige Enterprise para producción según https://docs.camunda.io/docs/reference/licenses/ (2026-11-07). Camunda 7 CE y Flowable OSS: licencia y estado de mantenimiento: comprobar al adoptarlos.
- **MUST** mantener el motor tras una interfaz propia (`ApprovalProcessPort`); el dominio no importa clases del motor.
- **MUST** versionar los `.bpmn` en el repo y migrar instancias en vuelo de forma explícita.
- **MUST** hacer idempotentes los service tasks (pueden reejecutarse tras fallo).
- **MUST NOT** meter reglas de negocio complejas en expresiones del BPMN; delegarlas a código testeado o `rules-engines`.
- **MUST NOT** compartir la BD del motor con tablas de negocio sin esquema separado.
- **SHOULD** usar correlación por `businessKey` y no guardar datos personales en variables de proceso.
- **SHOULD** definir timeouts y boundary events para tareas humanas.
