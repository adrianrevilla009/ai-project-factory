# Índice de skills

> Generado por `factory/tools/build_index.py`. No editar a mano.

Skills: **487** de 487 previstos en `catalog/skills-inventory.yaml`.

## 01-java-language (T1) — 14/14

- `code-style-and-naming` (T1) — Usar al nombrar, formatear y estructurar código Java (convenciones de nombres, tamaño de métodos, comentarios, imports y herramientas de formato automático).
- `collections-and-streams` (T1) — Usar al elegir colecciones, devolver listas o escribir pipelines de Streams en Java; cubre inmutabilidad, complejidad, efectos laterales y legibilidad.
- `equals-hashcode-tostring` (T1) — Usar al implementar o revisar equals, hashCode, toString y compareTo en clases Java, incluidas entidades JPA y records con datos sensibles.
- `exceptions-and-error-handling` (T1) — Usar al lanzar, capturar, envolver o registrar excepciones en Java; define jerarquía de dominio, causa original y límites donde se traducen.
- `generics-and-api-design` (T1) — Usar al diseñar APIs públicas Java, interfaces, genéricos, builders y firmas de métodos para que sean pequeñas, seguras en tipos y evolucionables.
- `immutability-and-value-objects` (T1) — Usar al diseñar clases de datos, DTOs, eventos o value objects para hacerlos inmutables, con copias defensivas e invariantes validadas en el constructor.
- `jvm-in-containers` (T1) — Usar al dimensionar o configurar la JVM en contenedores y Kubernetes (memoria, CPU, flags de heap, OOM, GC y límites de recursos coherentes).
- `logging-rules` (T1) — Usar al añadir o revisar logs en Java con SLF4J; define niveles, formato estructurado, correlación y qué nunca debe registrarse.
- `modern-java-idioms` (T1) — Usar al escribir o revisar Java nuevo para elegir records, sealed types, pattern matching, switch expressions, text blocks y var de forma idiomática.
- `no-lombok` (T1) — Usar siempre que se pueda introducir Lombok o sus anotaciones; indica las alternativas con records y builders explícitos (D27, ADR-0027).
- `null-safety` (T1) — Usar al escribir o revisar APIs, parámetros, retornos y uso de Optional en Java para evitar NullPointerException y definir el contrato de nulos.
- `profiling-and-leaks` (T1) — Usar al investigar latencia, uso de CPU/memoria, fugas de memoria o fugas de hilos y recursos en una aplicación Java; define método y herramientas.
- `strings-encoding-locale` (T1) — Usar al manipular String, bytes, charsets, formato de números/fechas, comparaciones de texto o regex en Java; evita bugs de codificación y de Locale.
- `time-and-money` (T1) — Usar al manejar fechas, zonas horarias, duraciones, relojes, importes o divisas en Java; evita java.util.Date, double para dinero y tiempo no testeable.

## 02-concurrency (T1) — 13/13

- `async-and-context-propagation` (T1) — Usar con @Async, executors y CompletableFuture cuando deban conservar seguridad, MDC, trace id o tenant; propagación de contexto entre hilos.
- `backpressure-and-bulkheads` (T1) — Usar al limitar carga y aislar fallos - colas acotadas, rate limiting, bulkheads (Resilience4j), rechazo temprano y degradación.
- `completablefuture-patterns` (T1) — Usar al componer tareas asíncronas con CompletableFuture - executor explícito, timeouts, manejo de errores y combinación.
- `concurrency-testing` (T1) — Usar al escribir tests de código concurrente - carreras, deadlocks, idempotencia bajo doble envío; sin sleeps, con latches y Awaitility.
- `concurrent-collections` (T1) — Usar al elegir colecciones compartidas entre hilos (ConcurrentHashMap, CopyOnWriteArrayList, BlockingQueue) y al hacer operaciones atómicas sobre ellas.
- `distributed-locking` (T1) — Usar al necesitar exclusión mutua entre varias instancias/pods (jobs únicos, recursos compartidos); locks con TTL, fencing tokens y alternativas.
- `idempotency-and-deduplication` (T1) — Usar al diseñar endpoints POST reintentables, consumidores de mensajes o jobs que pueden repetirse; claves de idempotencia y deduplicación.
- `java-memory-model` (T1) — Usar al compartir estado mutable entre hilos sin locks - visibilidad, happens-before, volatile, publicación segura e inmutabilidad.
- `locks-and-synchronization` (T1) — Usar al proteger estado compartido con synchronized, ReentrantLock, ReadWriteLock o atómicos; orden de locks, deadlocks y alcance.
- `scheduling-and-batch` (T1) — Usar al crear tareas @Scheduled, jobs periódicos o procesos batch (Spring Batch); ejecución única en clúster, idempotencia y reanudación.
- `structured-concurrency-and-scoped-values` (T1) — Usar al lanzar subtareas concurrentes que deben vivir y morir juntas, o al sustituir ThreadLocal por ScopedValue; estado de los JEP.
- `threads-executors-and-pools` (T1) — Usar al crear hilos, ExecutorService, pools o @Async en Java/Spring; define dimensionado, colas acotadas, nombres de hilo y cierre.
- `virtual-threads` (T1) — Usar al decidir si usar virtual threads (Java 21+) en Spring Boot o al migrar código bloqueante; cubre pinning, ThreadLocal y límites.

## 03-persistence-sql (T1) — 27/27

- `auditing-soft-delete-history` (T1) — Usar al añadir campos de auditoría, borrado lógico o historial de cambios a entidades SQL (Spring Data Auditing, Envers, tablas de historial).
- `batching-and-bulk-ops` (T1) — Usar al insertar, actualizar o borrar muchas filas con JPA/JDBC, o al configurar jdbc batch_size, bulk JPQL y procesos por lotes.
- `caching` (T1) — Usar al añadir caché a la capa de persistencia (Spring Cache, caché de 2º nivel de Hibernate, Redis/Caffeine) o al decidir si cachear.
- `connection-pooling` (T1) — Usar al configurar o diagnosticar el pool de conexiones (HikariCP) o al dimensionar conexiones a PostgreSQL por instancia y servicio.
- `data-privacy-in-db` (T1) — Usar al almacenar datos personales (PII) en SQL: clasificación, minimización, cifrado, enmascarado, retención y supresión.
- `db-design-conventions` (T1) — Usar al diseñar tablas, columnas, tipos y constraints en PostgreSQL: nombres, tipos de dinero/fecha, NOT NULL, claves y checks.
- `db-testing` (T1) — Usar al escribir tests de repositorios, migraciones y consultas contra PostgreSQL real con Testcontainers y @DataJpaTest.
- `id-generation` (T1) — Usar al elegir estrategia de clave primaria (secuencia, identity, UUID) o al exponer ids en APIs.
- `indexing-and-query-plans` (T1) — Usar al crear índices, diagnosticar consultas lentas o revisar planes de ejecución (EXPLAIN ANALYZE) en PostgreSQL.
- `isolation-levels-and-anomalies` (T1) — Usar al razonar sobre concurrencia en BD: niveles de aislamiento, anomalías (lost update, write skew) y cuándo subir el nivel.
- `jdbc-and-jooq` (T2) — Usar al elegir entre JPA, JdbcTemplate/JdbcClient y jOOQ, o al escribir consultas SQL explícitas, informes y lecturas complejas.
- `joins-and-fetch-joins` (T1) — Usar al escribir JPQL/Criteria con joins, JOIN FETCH, EntityGraph o al ver MultipleBagFetchException y paginación en memoria.
- `jpa-entity-design` (T1) — Usar al crear o modificar entidades JPA (mapeo, equals/hashCode, enums, relaciones, constructores).
- `lazy-vs-eager` (T1) — Usar al definir FetchType de asociaciones JPA y al tratar LazyInitializationException.
- `multi-tenancy` (T1) — Usar al diseñar o revisar aislamiento multi-tenant en SQL: discriminador/@TenantId, schema o BD por tenant, RLS, pools por tenant y tests de fugas.
- `n-plus-one` (T1) — Usar al escribir o revisar consultas JPA/Hibernate y mapeos de relaciones para evitar el problema N+1.
- `optimistic-locking` (T1) — Usar al proteger entidades de actualizaciones concurrentes con @Version y al manejar OptimisticLockException.
- `pagination` (T1) — Usar al paginar consultas en base de datos (offset vs keyset, Page vs Slice, orden estable, conteos costosos).
- `partitioning-and-archival` (T2) — Usar al decidir particionado de tablas grandes en PostgreSQL o una estrategia de retención, archivado y purga de datos.
- `persistence-context-and-flush` (T1) — Usar al razonar sobre el contexto de persistencia: dirty checking, flush, detached/managed, clear y save() de Spring Data.
- `pessimistic-locking` (T1) — Usar al necesitar bloqueo de filas (SELECT FOR UPDATE, SKIP LOCKED) por alta contención, colas en BD o deadlocks.
- `projections-and-dtos` (T1) — Usar al diseñar lecturas, listados o informes para decidir entre entidad, proyección Spring Data o DTO.
- `query-strategy` (T1) — Usar al elegir cómo expresar una consulta (derived query, @Query, Criteria/Specification, SQL nativo, jOOQ).
- `read-replicas-and-routing` (T2) — Usar al enrutar lecturas a réplicas de PostgreSQL (AbstractRoutingDataSource, readOnly) y al tratar el retraso de replicación.
- `schema-migrations` (T1) — Usar al crear o revisar migraciones de esquema con Flyway y al planificar cambios compatibles hacia atrás (expand/contract).
- `sql-injection-prevention` (T1) — Usar al escribir cualquier consulta SQL/JPQL/HQL, ordenaciones dinámicas o filtros que reciban entrada de usuario.
- `transactions` (T1) — Usar al definir límites transaccionales con @Transactional (propagación, rollback, self-invocation, llamadas externas).

## 04-spring-platform (T1) — 17/17

- `actuator-and-health` (T1) — Usar al configurar Spring Boot Actuator, health checks, liveness/readiness y exposición segura de endpoints de gestión.
- `configuration-properties` (T1) — Usar al añadir configuración a un servicio Spring Boot; propiedades tipadas con @ConfigurationProperties, validación y sin secretos en ficheros.
- `controllers-and-validation` (T1) — Usar al escribir o revisar controladores REST Spring MVC: controladores finos, DTOs de entrada/salida y validación Jakarta en el borde.
- `dependency-injection-rules` (T1) — Usar al escribir o revisar beans Spring: inyección por constructor, sin field injection, sin dependencias circulares ni service locator.
- `domain-events-in-spring` (T1) — Usar al publicar o consumir eventos de dominio dentro de una aplicación Spring (ApplicationEventPublisher, Spring Modulith) y decidir qué sale a mensajería externa.
- `error-handling-problem-details` (T1) — Usar al diseñar el manejo de errores HTTP en Spring: ProblemDetail (RFC 9457), @RestControllerAdvice y sin filtrar trazas.
- `file-upload-and-streaming` (T1) — Usar al recibir subidas multipart o servir descargas grandes en Spring (límites, almacenamiento, streaming) sin cargar ficheros completos en memoria.
- `graceful-shutdown-lifecycle` (T1) — Usar al configurar parada ordenada de servicios Spring Boot (server.shutdown=graceful), timeouts de fase y ciclo de vida de beans y tareas.
- `http-clients-and-timeouts` (T1) — Usar al crear o revisar llamadas HTTP salientes desde Spring (RestClient, WebClient, clientes declarativos) para fijar timeouts, pool y propagación de contexto.
- `mapping-mapstruct` (T1) — Usar al convertir entre entidades, DTOs y comandos en Java/Spring; MapStruct en tiempo de compilación, sin reflexión ni Lombok.
- `project-layout` (T1) — Usar al crear un servicio Spring Boot o añadir paquetes/módulos; define estructura por módulos de negocio con Spring Modulith.
- `reactive-vs-blocking` (T1) — Usar al decidir entre Spring MVC bloqueante (con hilos virtuales) y WebFlux reactivo para un servicio nuevo, o al mezclar ambos modelos.
- `resilience` (T1) — Usar al proteger llamadas a dependencias externas con Resilience4j (circuit breaker, retry, bulkhead, time limiter, rate limiter) en servicios Spring Boot.
- `spring-data-rules` (T1) — Usar al escribir repositorios y transacciones con Spring Data JPA: límites transaccionales, queries explícitas, open-in-view desactivado.
- `startup-and-native` (T1) — Usar al optimizar el arranque de una aplicación Spring Boot o al evaluar compilación nativa GraalVM, AOT, CDS o lazy initialization.
- `testing-slices` (T1) — Usar al escribir tests de Spring Boot para elegir el slice mínimo (@WebMvcTest, @DataJpaTest, @JsonTest) en lugar de @SpringBootTest completo.
- `upgrade-policy` (T1) — Usar al actualizar Spring Boot, Spring Framework o Java en un proyecto, o al fijar la política de versiones y soporte del stack.

## 05-architecture (T1) — 26/26

- `anti-corruption-layer` (T1) — Usar al integrar con un sistema legado o externo cuyo modelo no debe contaminar el dominio propio.
- `bff-and-api-gateway` (T1) — Usar al diseñar el punto de entrada de APIs con API gateway, BFF por cliente y qué lógica puede vivir en cada uno.
- `cell-based-architecture` (T1) — Usar al diseñar aislamiento de fallos por celdas (particiones independientes de la plataforma) para limitar el radio de impacto.
- `clean-architecture` (T1) — Usar al decidir la dirección de dependencias entre entidades, casos de uso, adaptadores y frameworks; complementa hexagonal.
- `code-smells-and-refactoring` (T1) — Usar al revisar código con olores (métodos largos, clases dios, duplicación) y al refactorizar con seguridad.
- `connascence-and-coupling` (T1) — Usar al evaluar acoplamiento entre módulos o servicios, o al decidir dónde está justificado el acoplamiento fuerte; guía el diseño de dependencias.
- `consistency-and-cap-tradeoffs` (T1) — Usar al decidir niveles de consistencia, replicación o fronteras transaccionales en sistemas distribuidos; aplica CAP/PACELC de forma práctica.
- `cqrs` (T1) — Usar al decidir si separar modelos de escritura y lectura (CQRS) y cómo mantener las proyecciones sin doble escritura.
- `ddd-strategic` (T1) — Usar al delimitar dominios, bounded contexts y relaciones entre equipos o servicios, antes de decidir módulos o microservicios.
- `ddd-tactical` (T1) — Usar al modelar el dominio dentro de un bounded context: entidades, value objects, aggregates, repositorios y servicios de dominio.
- `event-driven` (T1) — Usar al diseñar comunicación asíncrona por eventos o mensajes entre módulos o servicios: contratos, outbox, idempotencia y entrega.
- `event-sourcing` (T1) — Usar al evaluar o implementar event sourcing (estado como secuencia de eventos); por defecto se desaconseja salvo necesidad de auditoría o temporalidad.
- `evolutionary-architecture-fitness-functions` (T1) — Usar al definir cómo se protegen automáticamente las características de la arquitectura (dependencias, rendimiento, seguridad) mediante fitness functions en CI.
- `gof-patterns-in-practice` (T1) — Usar al plantearse un patrón GoF (strategy, factory, decorator...) en Java/Spring y decidir si realmente aporta.
- `hexagonal` (T1) — Usar al estructurar un servicio Spring Boot con puertos y adaptadores para aislar el dominio de web, base de datos y mensajería.
- `layering-rules-archunit` (T1) — Usar al fijar o revisar reglas de capas, ciclos y dependencias permitidas con ArchUnit en un servicio Java.
- `microservices-decision-guide` (T1) — Usar al decidir si extraer un servicio o partir un monolito en microservicios; da criterios y un registro de decisión.
- `modular-monolith` (T1) — Usar al estructurar un sistema como un único despliegue con módulos de negocio aislados antes de (o en lugar de) separar en microservicios.
- `multi-tenant-architecture` (T1) — Usar al diseñar un sistema que sirve a varios clientes (tenants): modelo de aislamiento de datos, identificación del tenant y límites por tenant.
- `quality-attributes-atam` (T1) — Usar al definir atributos de calidad medibles y evaluar compromisos arquitectónicos (ATAM) antes de fijar una arquitectura.
- `sagas-and-process-managers` (T1) — Usar al coordinar una operación de negocio que abarca varios servicios o aggregates sin transacción distribuida: sagas, compensaciones, timeouts.
- `scalability-patterns` (T1) — Usar al diseñar o revisar cómo escala un servicio: statelessness, caché, colas, particionado, backpressure y límites de capacidad.
- `solid` (T1) — Usar al diseñar o revisar clases Java (responsabilidades, extensión, sustitución, interfaces e inversión de dependencias).
- `strangler-fig-migration` (T1) — Usar al migrar un sistema legado de forma incremental, redirigiendo funcionalidad al nuevo sistema sin reescritura big-bang.
- `tech-debt-management` (T1) — Usar al registrar, priorizar o pagar deuda técnica y al decidir si un atajo es aceptable; define registro, intereses y presupuesto.
- `twelve-factor` (T1) — Usar al diseñar, configurar o revisar servicios cloud-native: configuración por entorno, procesos stateless, logs, build/release/run y paridad dev-prod.

## 06-api-and-integration (T1) — 20/20

- `api-versioning-deprecation` (T1) — Usar al decidir cómo versionar una API pública o interna y al deprecar y retirar versiones u operaciones.
- `asyncapi-event-contracts` (T1) — Usar al definir o cambiar eventos/mensajes asíncronos (Kafka, SQS, RabbitMQ): contrato AsyncAPI, envelope y naming.
- `backward-compatibility-rules` (T1) — Usar al modificar cualquier contrato (OpenAPI, Protobuf, GraphQL, eventos) para decidir si el cambio es compatible o rompiente.
- `batch-file-sftp-integration` (T1) — Usar al integrar por ficheros (CSV/XML) vía SFTP o almacenamiento compartido con Spring Batch: atomicidad, checksums, reinicio e idempotencia.
- `contract-testing-pact` (T1) — Usar al implantar contract testing consumer-driven con Pact (JVM): contratos, verificación del proveedor, broker y can-i-deploy.
- `delivery-semantics` (T1) — Usar al decidir garantías de entrega (at-least-once, exactly-once efectivo), consumidores idempotentes y patrón outbox entre servicios.
- `dlq-retries-poison-messages` (T1) — Usar al diseñar reintentos, dead-letter queues y manejo de mensajes venenosos en consumidores Kafka, RabbitMQ o SQS.
- `graphql` (T1) — Usar al exponer o consumir una API GraphQL (Spring for GraphQL): esquema, N+1, límites de consulta, errores y autorización.
- `grpc-protobuf` (T1) — Usar al definir o cambiar servicios gRPC y mensajes Protobuf (diseño de .proto, números de campo, errores, deadlines).
- `idempotency-keys` (T1) — Usar al diseñar POST/acciones con efectos que un cliente puede reintentar (pagos, pedidos) o consumidores que pueden recibir duplicados.
- `kafka-producers-consumers` (T1) — Usar al escribir o revisar productores y consumidores Kafka con Spring Kafka (acks, idempotencia, commits de offsets, claves, concurrencia).
- `openapi-contract-first` (T1) — Usar al crear o cambiar una API HTTP: el contrato OpenAPI se escribe y revisa antes que el código y se valida en CI.
- `pagination-filter-sort` (T1) — Usar al exponer colecciones en una API: paginación (offset o cursor), filtros y ordenación con límites seguros.
- `rabbitmq-sqs` (T1) — Usar al elegir o configurar colas RabbitMQ o Amazon SQS (acks, visibility timeout, DLQ, FIFO) y su equivalente local.
- `rate-limiting-quotas` (T1) — Usar al definir límites de tasa y cuotas por cliente de una API y cómo comunicarlos (429, Retry-After) en gateway o servicio.
- `rest-design-guidelines` (T1) — Usar al diseñar o revisar endpoints REST (recursos, verbos, códigos HTTP, errores) de un servicio Spring Boot.
- `schema-registry-and-evolution` (T1) — Usar al definir o cambiar esquemas de eventos (Avro/Protobuf/JSON Schema) y modos de compatibilidad en un schema registry.
- `sdk-generation` (T1) — Usar al generar SDKs/clientes de API desde OpenAPI (Java, TypeScript): herramienta, versionado, módulo separado y qué no editar a mano.
- `soap-legacy-integration` (T1) — Usar al consumir o exponer servicios SOAP/WSDL de sistemas heredados: contrato WSDL, XXE, timeouts y capa anticorrupción.
- `webhooks` (T1) — Usar al emitir o recibir webhooks: firma HMAC, anti-replay, reintentos, idempotencia y protección SSRF.

## 07-appsec (T1) — 26/26

- `asvs-mapping` (T1) — Usar al fijar el nivel OWASP ASVS de un servicio y trazar requisitos de seguridad a código y tests; para backlog de seguridad y revisiones de diseño.
- `audit-trail-and-security-logging` (T1) — Usar al decidir qué eventos de seguridad y auditoría registrar, con qué campos, y cómo protegerlos de manipulación y de fugas de datos.
- `authn-oidc-oauth2` (T1) — Usar al integrar autenticación con Keycloak/OIDC y OAuth2 en Spring Boot y React: flujos, PKCE, validación de tokens, resource server y logout.
- `authz-rbac-abac-rebac` (T1) — Usar al diseñar o revisar autorización: elegir RBAC, ABAC o ReBAC, aislamiento por tenant, denegar por defecto y evitar IDOR/BOLA en servicios Spring Boot.
- `cloud-iam-least-privilege` (T1) — Usar al escribir políticas IAM, roles de servicio o permisos de AWS (Terraform o consola) para aplicar mínimo privilegio y evitar comodines.
- `container-and-k8s-security` (T1) — Usar al escribir Dockerfile o manifiestos Kubernetes/Helm para endurecer imágenes, pods, red y RBAC del clúster.
- `crypto-tls-mtls-key-rotation` (T1) — Usar al cifrar o firmar datos, hashear contraseñas, configurar TLS/mTLS o diseñar la rotación de claves y certificados.
- `dependency-security` (T1) — Usar al añadir, actualizar o auditar dependencias Maven/npm y al gestionar CVE conocidos en bibliotecas de terceros.
- `deserialization-xxe-ssrf-traversal` (T1) — Usar al deserializar datos externos, parsear XML, llamar a URLs aportadas por el usuario o resolver rutas de fichero, para evitar RCE, XXE, SSRF y path traversal.
- `dos-and-rate-limiting` (T1) — Usar al diseñar límites de tasa, tamaños, timeouts, paginación y protección frente a abuso o denegación de servicio en APIs Java/Spring.
- `file-upload-security` (T1) — Usar al implementar subida o descarga de ficheros (multipart, URLs prefirmadas) para validar tipo, tamaño, nombre y almacenamiento seguro.
- `injection-families` (T1) — Usar al construir consultas SQL/JPQL, NoSQL, LDAP, comandos de SO, plantillas o expresiones SpEL con datos externos, para prevenir inyección.
- `input-validation-output-encoding` (T1) — Usar al recibir datos externos (API, formularios, ficheros, colas) y al renderizarlos: validación con Bean Validation, listas permitidas y codificación según contexto (XSS).
- `jwt-and-sessions` (T1) — Usar al emitir, validar o almacenar JWT, cookies de sesión y refresh tokens: algoritmos, claims, caducidad, revocación y flags de cookie.
- `llm-security` (T1) — Usar al integrar un LLM o agente en una aplicación (RAG, tools, MCP) para defenderse de inyección de prompt, fuga de datos y acciones excesivas.
- `method-and-endpoint-security` (T1) — Usar al configurar Spring Security (SecurityFilterChain, method security, actuator) para exigir autenticación y permisos por endpoint y método con denegación por defecto.
- `owasp-top10-and-api-top10` (T1) — Usar al revisar o diseñar APIs y apps web frente a OWASP Top 10 y API Security Top 10; mapa de riesgos a skills y controles concretos.
- `pii-and-data-classification` (T1) — Usar al diseñar modelos de datos, logs, APIs o exportaciones que contengan datos personales, para clasificarlos, minimizarlos y protegerlos.
- `secrets-management` (T1) — Usar al manejar contraseñas, tokens, claves API o certificados en código, configuración, CI o despliegue, y al elegir dónde guardarlos y cómo rotarlos.
- `secure-sdlc-nist-ssdf` (T1) — Usar al definir o revisar el ciclo de desarrollo seguro de un proyecto y su trazabilidad con NIST SSDF (SP 800-218): prácticas, evidencias y gates por fase.
- `security-headers-cors-csrf` (T1) — Usar al configurar cabeceras HTTP de seguridad, CORS y protección CSRF en Spring Boot y SPA React, incluyendo CSP, HSTS y cookies SameSite.
- `security-testing-sast-dast` (T1) — Usar al definir pruebas de seguridad en CI: SAST (Semgrep), DAST (ZAP), secretos, dependencias y gates con umbrales, triaje de falsos positivos.
- `supply-chain` (T1) — Usar al definir cómo se construyen, firman y verifican artefactos e imágenes (SBOM, niveles SLSA, firmas con cosign).
- `threat-modeling-stride` (T1) — Usar al diseñar un servicio, flujo o integración nuevos para identificar amenazas con STRIDE sobre un diagrama de flujo de datos y registrar mitigaciones.
- `vulnerability-sla-and-incident-response` (T1) — Usar al triar vulnerabilidades, fijar plazos de corrección (SLA) o responder a un incidente de seguridad con contención, comunicación y post-mortem.
- `zero-trust` (T1) — Usar al diseñar la arquitectura de red e identidad de servicios: no confiar en la red interna, identidad por carga de trabajo, mTLS con Istio y mínimo privilegio.

## 08-testing-quality (T1) — 22/22

- `api-testing` (T1) — Usar al probar endpoints REST de un servicio Spring: estado, cuerpo, Problem Details, validación, seguridad y paginación, con MockMvc o RestAssured.
- `architecture-testing-archunit` (T1) — Usar al convertir reglas de arquitectura (capas, dependencias, ciclos, nombres) en tests ArchUnit ejecutados en cada build.
- `bdd` (T1) — Usar al convertir criterios de aceptación en escenarios Given/When/Then ejecutables (Cucumber u homólogo) o al decidir si BDD aporta valor.
- `canary-analysis-and-synthetic-monitoring` (T1) — Usar al definir el análisis automático de un canary (métricas, umbrales, rollback) y las comprobaciones sintéticas que vigilan flujos críticos tras un despliegue.
- `chaos-engineering` (T1) — Usar al diseñar experimentos de caos y game days: Chaos Monkey for Spring Boot, Chaos Mesh, Toxiproxy, hipótesis, radio de explosión y abortado.
- `code-review-guidelines` (T1) — Usar al revisar un pull request o preparar uno para revisión: qué mirar, en qué orden, tamaño del PR y cómo formular comentarios.
- `contract-testing` (T1) — Usar al decidir cómo verificar contratos entre servicios o eventos (consumer-driven, OpenAPI, AsyncAPI) y qué herramienta aplicar en cada caso.
- `coverage-policy` (T1) — Usar al definir o revisar umbrales de cobertura (JaCoCo), exclusiones y cómo interpretar la cobertura en CI sin convertirla en objetivo vacío.
- `e2e-testing` (T1) — Usar al diseñar o escribir tests end-to-end de flujos críticos (UI y API encadenada) y decidir qué NO debe cubrirse a ese nivel.
- `flaky-test-management` (T1) — Usar cuando un test falla de forma intermitente, al diagnosticar tests inestables o antes de poner reintentos, @Disabled o quarantine.
- `integration-testing-testcontainers` (T1) — Usar al escribir tests de integración que necesitan PostgreSQL, Kafka, Redis u otro servicio real, con Testcontainers y Spring Boot.
- `localstack-aws` (T1) — Usar al probar código que usa S3, SQS, SNS, DynamoDB u otros servicios AWS con LocalStack en local o CI, y para saber qué NO reproduce.
- `mutation-testing` (T1) — Usar al medir la calidad real de los tests unitarios con PIT (pitest) en módulos Java de lógica de dominio y definir umbrales.
- `performance-testing` (T1) — Usar al planificar o ejecutar pruebas de rendimiento con JMeter: baseline, carga, soak y spike, con criterios de aceptación y entorno comparable.
- `property-based-testing` (T1) — Usar al testear invariantes, parsers, serialización o reglas con muchos casos límite con jqwik (propiedades y generadores) en vez de ejemplos fijos.
- `resilience-testing` (T1) — Usar al escribir tests automáticos que comprueban timeouts, retries, circuit breaker, bulkheads y degradación ante fallos de dependencias.
- `static-analysis` (T1) — Usar al configurar o revisar el análisis estático en Maven (Checkstyle, PMD, SpotBugs, Error Prone) y los quality gates que bloquean el build.
- `tdd` (T1) — Usar al implementar lógica de dominio o corregir un bug: ciclo rojo-verde-refactor con tests primero y pasos pequeños.
- `test-data-management` (T1) — Usar al crear datos de prueba: builders, fixtures, datasets de integración, anonimización de datos reales y limpieza entre tests.
- `test-strategy` (T1) — Usar al definir o revisar qué tipos de test escribir, en qué proporción y en qué fase del pipeline se ejecutan (pirámide, slices, E2E mínimos).
- `unit-testing-java` (T1) — Usar al escribir o revisar tests unitarios Java con JUnit 5, AssertJ y Mockito: estructura, nombres, dobles y qué NO mockear.
- `wiremock-and-stubbing` (T1) — Usar al probar clientes HTTP contra APIs de terceros o internas simuladas con WireMock: stubs, verificación, fallos y latencia.

## 09-build-supply-chain (T1) — 15/15

- `bom-management` (T1) — Usar al fijar versiones de dependencias con un BOM corporativo: importación, overrides, actualización y publicación del BOM.
- `build-caching-and-speed` (T1) — Usar al acelerar builds Maven o CI: caché de dependencias, builds paralelos, build incremental, caché de capas Docker, sin perder reproducibilidad ni correctitud.
- `container-images` (T1) — Usar al escribir Dockerfiles o construir imágenes de servicios Spring Boot: base mínima, usuario no root, multi-stage, digest fijado, capas, escaneo y firma.
- `dependency-hygiene` (T1) — Usar al añadir, quitar o revisar dependencias Maven/npm: mínimas, declaradas, sin no usadas, sin transitivas implícitas y con lockfile.
- `enforcer-rules` (T1) — Usar al configurar maven-enforcer-plugin en el parent: versiones mínimas, convergencia, librerías prohibidas (Lombok) y reglas de release.
- `jdk-distribution-and-upgrade-cadence` (T1) — Usar al elegir distribución y versión de JDK, o al planificar una subida de JDK LTS, parches trimestrales y compatibilidad con Spring Boot y librerías.
- `license-compliance` (T1) — Usar al añadir dependencias, montar el informe de licencias en el build o revisar si una licencia de terceros es aceptable (AGPL, SSPL, GPL, licencias de pago).
- `maven-multimodule-layout` (T1) — Usar al estructurar o revisar un proyecto Maven multimódulo: módulos, aggregator vs parent, dependencias entre módulos y límites de arquitectura.
- `maven-wrapper-and-toolchains` (T1) — Usar al configurar cómo se invoca Maven (mvnw) y qué JDK compila el proyecto: Maven Wrapper, toolchains.xml y consistencia entre local y CI.
- `parent-pom` (T1) — Usar al crear o modificar el parent POM corporativo o el pom raíz: propiedades, pluginManagement, perfiles y herencia de Spring Boot.
- `release-automation` (T1) — Usar al diseñar el pipeline de release: versión desde Conventional Commits, changelog, tag, artefactos firmados con SBOM y publicación sin pasos manuales ni despliegue desde la fábrica.
- `renovate-dependabot-policy` (T1) — Usar al configurar actualización automática de dependencias (Renovate o Dependabot): agrupación, cadencia, automerge y reglas de revisión.
- `reproducible-builds` (T1) — Usar al configurar el build Maven/Docker para que el mismo commit produzca artefactos idénticos bit a bit: timestamp, orden, versiones fijas.
- `sbom-generation` (T1) — Usar al generar, versionar o publicar el SBOM CycloneDX de un servicio Java o de una imagen, o al configurar el plugin CycloneDX en Maven y en CI.
- `versioning-semver-snapshots` (T1) — Usar al versionar artefactos y servicios: SemVer, SNAPSHOT vs release, CI-friendly versions (revision) y reglas de inmutabilidad.

## 10-observability-app (T1) — 12/12

- `alerting-symptom-based` (T1) — Usar al escribir o revisar alertas Prometheus/Alertmanager: alertar por síntomas del usuario, severidades, ruido, burn rate y enrutado.
- `db-and-kafka-observability` (T1) — Usar al observar acceso a base de datos y Kafka desde la aplicación: latencia de queries, pool, lag de consumidores, reintentos y DLQ.
- `golden-signals-red-use` (T1) — Usar al diseñar dashboards y métricas base de un servicio: golden signals, método RED para servicios y USE para recursos.
- `jvm-observability` (T1) — Usar al definir qué observar de la JVM en producción: memoria, GC, hilos, pools, JFR y volcados, en contenedores Kubernetes.
- `llm-observability` (T1) — Usar al instrumentar llamadas a LLM en una aplicación: trazas, tokens, latencia, coste, calidad y privacidad de prompts.
- `metrics-micrometer` (T1) — Usar al crear o revisar métricas de aplicación con Micrometer en Spring Boot: nombres, tags, cardinalidad, histogramas y exposición Prometheus.
- `on-call-and-runbook-links` (T1) — Usar al preparar un servicio para guardia: runbooks enlazados desde alertas y dashboards, rotación, escalado y postmortems sin culpas.
- `otel-fundamentals-and-semconv` (T1) — Usar al diseñar o revisar la telemetría de un servicio con OpenTelemetry: señales, Resource, convenciones semánticas, Collector y OTLP.
- `otel-java-agent-vs-sdk` (T1) — Usar al decidir cómo instrumentar un servicio Spring Boot con OpenTelemetry: agente Java, starter/SDK o puente Micrometer Tracing.
- `slo-sli-error-budgets` (T1) — Usar al definir SLIs, SLOs y presupuestos de error de un servicio, y al conectarlos con alertas, releases y el tier de resiliencia.
- `structured-logging` (T1) — Usar al configurar logs JSON, correlación con trace_id y envío a Loki en servicios Spring Boot; complementa logging-rules.
- `tracing` (T1) — Usar al añadir spans, propagación de contexto W3C y muestreo de trazas distribuidas (Tempo) en servicios HTTP, Kafka y asíncronos.

## 11-aws-governance (T1) — 11/11

- `break-glass-and-jit-access` (T1) — Usar al diseñar acceso privilegiado a AWS de emergencia (break-glass) y elevación temporal just-in-time, con auditoría y alertas.
- `compliance-as-code` (T1) — Usar al convertir requisitos de cumplimiento AWS en controles verificables: Config rules, conformance packs, Checkov/Conftest en CI y evidencias.
- `control-tower-and-account-factory` (T1) — Usar al decidir cómo crear y gobernar cuentas AWS nuevas: Control Tower, Account Factory (AFT) o Terraform propio, y landing zone en eu-west-1.
- `identity-center-sso` (T1) — Usar al diseñar el acceso humano a cuentas AWS con IAM Identity Center: grupos, permission sets, federación con Keycloak y sesiones cortas.
- `kms-multi-region-keys` (T1) — Usar al diseñar claves AWS KMS: CMK por dominio, claves multi-región entre eu-west-1 y eu-central-1, key policies y rotación.
- `log-archive-and-audit-account` (T1) — Usar al diseñar las cuentas log-archive y audit de AWS: buckets inmutables de logs, retención, replicación entre regiones y acceso de solo lectura.
- `org-cloudtrail-config-securityhub-guardduty` (T1) — Usar al diseñar la detección y auditoría a nivel organización en AWS: CloudTrail org, AWS Config, Security Hub y GuardDuty con administrador delegado.
- `organization-and-ou-design` (T1) — Usar al diseñar la estructura de AWS Organizations (cuentas y OUs) de un proyecto: separación por entorno, carga de trabajo, seguridad y logging.
- `regions-and-data-residency` (T1) — Usar al decidir regiones AWS y residencia de datos: eu-west-1 primaria, eu-central-1 secundaria, qué replica y qué no, y disponibilidad de servicios.
- `scp-guardrails` (T1) — Usar al escribir o revisar Service Control Policies de AWS Organizations: denegación de regiones, protección de trails, KMS y root.
- `tagging-cost-allocation-budgets` (T1) — Usar al definir tags obligatorios, asignación de costes y AWS Budgets en cuentas AWS; también al revisar Terraform sin default_tags.

## 12-aws-networking (T1) — 11/11

- `alb-nlb-and-tls-termination` (T1) — Usar al elegir y configurar balanceadores AWS (ALB vs NLB), listeners, certificados ACM y dónde terminar TLS (borde, balanceador o malla).
- `cidr-planning-and-ipam` (T1) — Usar al diseñar rangos CIDR de VPC, subredes o EKS, o al introducir VPCs nuevas que deban conectarse por TGW, peering o VPN sin solapamientos.
- `cross-region-connectivity-and-cost` (T1) — Usar al conectar eu-west-1 con eu-central-1 o estimar costes de red: peering TGW, transferencia entre AZ/regiones, NAT, endpoints y replicación.
- `dns-route53-private-and-hybrid` (T1) — Usar al diseñar DNS en AWS: zonas privadas de Route 53, Resolver inbound/outbound para híbrido, asociación entre VPC/cuentas y registros de failover.
- `eks-networking` (T1) — Usar al diseñar la red de EKS: VPC CNI, agotamiento de IPs de pods, security groups, AWS Load Balancer Controller, endpoint del API y etiquetas de subredes.
- `flow-logs-and-network-observability` (T1) — Usar al activar o revisar VPC Flow Logs, logs de DNS/ALB/WAF y diagnóstico de red en AWS: destino, formato, retención, coste y alertas.
- `global-accelerator-and-failover-routing` (T1) — Usar al diseñar la entrada multirregión eu-west-1/eu-central-1: elegir entre Route 53 (failover, latencia) y Global Accelerator, health checks y reparto de tráfico.
- `private-endpoints-and-egress-control` (T1) — Usar al diseñar el acceso privado a servicios AWS (VPC endpoints) y la salida a Internet (NAT, egress centralizado, allowlist de dominios) desde subredes privadas.
- `transit-gateway-hub-and-spoke` (T1) — Usar al conectar varias VPC o cuentas con Transit Gateway: tablas de rutas segmentadas, inspección centralizada y peering entre eu-west-1 y eu-central-1.
- `vpc-multi-az-layers` (T1) — Usar al diseñar la topología de una VPC: capas de subredes (pública, privada, datos), reparto en AZ, NAT, tablas de rutas y security groups.
- `waf-shield-and-cloudfront` (T1) — Usar al proteger endpoints públicos en AWS: AWS WAF, Shield, CloudFront delante de ALB/S3, bloqueo de acceso directo al origen y reglas de tasa.

## 13-kubernetes-and-istio (T1) — 27/27

- `authorization-policies` (T1) — Usar al escribir AuthorizationPolicy de Istio: deny-all por defecto, allow por identidad de servicio y reglas L7 mínimas.
- `autoscaling` (T1) — Usar al configurar HPA, VPA o KEDA para escalar pods Spring Boot por CPU, memoria, métricas propias o eventos (colas Kafka), junto al autoscaler de nodos.
- `backup-and-restore` (T1) — Usar al diseñar backups de recursos y volúmenes de Kubernetes con Velero (OSS), programación, retención y pruebas de restauración.
- `canary-and-traffic-splitting` (T1) — Usar al desplegar progresivamente (canary, blue/green, mirroring) con reparto de tráfico por pesos en Istio o Gateway API.
- `cluster-addons-baseline` (T1) — Usar al definir el conjunto mínimo de addons de un clúster Kubernetes: cert-manager, external-dns, external-secrets, metrics-server, CNI/CSI, y su ciclo de vida.
- `cluster-topology` (T1) — Usar al decidir cuántos clústeres Kubernetes, por entorno/región/cell, y qué va en cada uno antes de definir infraestructura EKS o local (kind/k3d).
- `cluster-upgrades-and-drift` (T1) — Usar al planificar upgrades de versión de Kubernetes/EKS, nodos y addons, o al detectar y corregir drift entre el estado deseado en Git/IaC y el clúster.
- `cost-visibility` (T1) — Usar al definir etiquetado, asignación de costes y visibilidad de gasto por namespace/equipo en Kubernetes con OpenCost.
- `gateway-api` (T1) — Usar al exponer servicios HTTP con Kubernetes Gateway API (Gateway, HTTPRoute) y decidir su relación con los recursos Istio.
- `helm-standards` (T1) — Usar al crear o revisar charts Helm: estructura, values, versionado, schema, lint y reglas para no meter secretos ni lógica excesiva en templates.
- `ingress-and-egress-gateways` (T1) — Usar al configurar la entrada y salida de tráfico de la malla Istio: gateway de ingress, egress controlado y ServiceEntry.
- `istio-upgrades-and-ops` (T1) — Usar al instalar, actualizar o operar Istio: upgrades por revisión (canary), compatibilidad de versiones y comprobaciones previas.
- `kustomize-overlays` (T1) — Usar al organizar manifiestos con Kustomize: base y overlays por entorno, patches, generators y cuándo preferirlo o combinarlo con Helm.
- `mesh-observability` (T2) — Usar al configurar métricas, trazas y visualización de la malla Istio con Prometheus, tracing y Kiali.
- `mesh-vs-app-resilience` (T1) — Usar al decidir dónde implementar reintentos, timeouts y circuit breaking (malla Istio o aplicación) para no duplicar reintentos.
- `mtls-strict-and-peer-auth` (T1) — Usar al activar o auditar mTLS en la malla Istio: PeerAuthentication STRICT, migración desde PERMISSIVE y excepciones por puerto.
- `multi-cluster-and-dr` (T1) — Usar al diseñar recuperación ante desastres o despliegue multi-clúster/multi-región en Kubernetes: patrones activo-pasivo y activo-activo, estado y conmutación.
- `multi-cluster-mesh` (T2) — Usar al valorar o diseñar una malla Istio que abarque varios clústeres: modelos, confianza compartida y descubrimiento de servicios.
- `namespaces-quotas-multitenancy` (T1) — Usar al crear namespaces por equipo/servicio/entorno con ResourceQuota, LimitRange, NetworkPolicy por defecto y aislamiento multi-tenant en Kubernetes.
- `node-pools-and-capacity` (T1) — Usar al definir node pools/grupos de nodos, tamaños, taints, spot vs on-demand y headroom de capacidad de un clúster Kubernetes (EKS).
- `operators` (T1) — Usar al adoptar operators en Kubernetes (CloudNativePG para Postgres, Strimzi para Kafka): criterios de elección, CRDs, upgrades y operación segura.
- `pod-security-and-admission` (T1) — Usar al configurar Pod Security Admission, Kyverno o ValidatingAdmissionPolicy para imponer reglas a los pods en el clúster; modos audit, warn y enforce.
- `rbac-and-service-accounts` (T1) — Usar al definir Roles, RoleBindings y ServiceAccounts de Kubernetes, o al enlazar pods con IAM de nube (IRSA/Pod Identity) con mínimo privilegio.
- `runtime-security` (T1) — Usar al desplegar o configurar detección de amenazas en runtime en Kubernetes con Falco: reglas, salidas de alertas y ajuste de falsos positivos.
- `sidecar-vs-ambient-decision` (T1) — Usar al elegir o revisar el modo de dataplane de Istio (sidecar o ambient) según ADR-0032; por defecto sidecar.
- `traffic-management` (T1) — Usar al definir VirtualService, DestinationRule, timeouts, outlier detection y pools de conexión en Istio.
- `workload-baseline` (T1) — Usar al escribir o revisar Deployments/StatefulSets: requests/limits, probes, PDB, topology spread y seccomp RuntimeDefault para servicios Spring Boot.

## 14-secrets-and-config (T1) — 15/15

- `audit-and-break-glass` (T1) — Usar al configurar auditoría de Vault (audit devices) y al diseñar el acceso de emergencia (break-glass, root token, claves de unseal) con trazabilidad.
- `auth-methods` (T1) — Usar al decidir cómo se autentican personas, pods y pipelines contra Vault (Kubernetes auth, JWT/OIDC con Keycloak, AppRole) y qué TTL y bindings aplicar.
- `config-by-environment` (T1) — Usar al organizar la configuración por entorno (dev/stage/prod) con GitOps + Vault (D11): qué va en Git, qué en Vault y cómo se inyecta en Spring Boot.
- `deployment-ha` (T1) — Usar al diseñar o revisar el despliegue de Vault OSS: Raft de 3 AZ, auto-unseal con KMS y un clúster independiente por región (sin replicación Enterprise).
- `dynamic-database-credentials` (T1) — Usar al configurar el motor de BD de Vault (credenciales dinámicas o roles estáticos) y al planificar su comportamiento en failover de Aurora Global.
- `envelope-encryption-and-kms` (T1) — Usar al cifrar datos de aplicación con cifrado de sobre (DEK/KEK), KMS y claves multi-región, y al decidir entre Vault Transit y KMS para datos entre regiones.
- `feature-flags-openfeature` (T1) — Usar al introducir feature flags en un servicio Java: API OpenFeature, providers, contexto de evaluación, ciclo de vida y limpieza de flags.
- `injection-patterns` (T1) — Usar al decidir cómo llegan los secretos de Vault a un pod en Kubernetes: Vault Secrets Operator, Agent Injector o CSI Provider, y cómo los consume Spring Boot.
- `pki-and-cert-issuance` (T1) — Usar al emitir certificados internos con el motor PKI de Vault (CA raíz offline, intermedia por región, roles y TTL cortos) y al integrarlos con cert-manager.
- `policies` (T1) — Usar al escribir o revisar políticas ACL de Vault (paths, capabilities, templating por identidad) para dar mínimo privilegio a servicios, CI y operadores.
- `rotation-and-leases` (T1) — Usar al diseñar la rotación de secretos y el ciclo de vida de leases de Vault (TTL, renovación, revocación) y la tolerancia de las apps a credenciales que cambian.
- `secret-scanning-and-leak-response` (T1) — Usar al configurar escaneo de secretos (pre-commit, CI, histórico) y al responder a una fuga: revocar, rotar, investigar y prevenir recurrencia.
- `spring-cloud-config-module` (T1) — Usar al decidir si añadir Spring Cloud Config Server (módulo opcional, D11) frente a GitOps + Vault, y al configurarlo si se adopta.
- `transit-encryption` (T1) — Usar al cifrar datos con el motor Transit de Vault y al decidir si un dato puede leerse desde varias regiones (Transit no comparte claves entre clústeres).
- `vault-and-keycloak-dr` (T1) — Usar al diseñar backup, restauración y recuperación ante desastres de Vault OSS (un clúster por región) y de Keycloak, incluidos RPO/RTO y ensayos.

## 15-artifacts-and-registry (T1) — 11/11

- `admission-verification` (T1) — Usar al definir qué imágenes admite el clúster: Kyverno verifyImages (firma, digest, atestaciones) y registros permitidos antes de ejecutar pods.
- `artifact-repository-port` (T1) — Usar al diseñar o cambiar cómo el pipeline publica, promueve, retiene y traza artefactos (imágenes OCI, JAR, npm) tras un puerto agnóstico del repositorio.
- `docker-multistage` (T1) — Usar al escribir o revisar un Dockerfile de Java o React: multi-stage, imagen mínima, usuario no root, FS de solo lectura, caché de capas, labels y multi-arch.
- `image-scanning` (T1) — Usar al configurar el escaneo de vulnerabilidades de imágenes y dependencias con Trivy o Grype: umbrales, exclusiones con caducidad y gate de CI.
- `image-signing-and-provenance` (T1) — Usar al firmar imágenes con cosign (keyless OIDC) y emitir atestaciones de procedencia SLSA y SBOM en el pipeline de release.
- `license-policy` (T1) — Usar al decidir qué licencias de dependencias se permiten, cómo se comprueban a partir del SBOM y cómo se gestionan excepciones (copyleft, no comerciales).
- `promotion-between-environments` (T1) — Usar al definir cómo un artefacto avanza de dev a staging y prod: misma imagen por digest, sin rebuild, con gates y evidencias.
- `remote-repos-and-dependency-confusion-protection` (T1) — Usar al configurar proxies de Maven/npm/OCI y repos virtuales para evitar dependency confusion, typosquatting y descargas directas de internet.
- `retention-and-cleanup` (T1) — Usar al definir políticas de retención y limpieza de imágenes y paquetes (Harbor, Nexus, ECR) sin romper rollback ni trazabilidad.
- `sbom` (T1) — Usar al generar, almacenar y consumir SBOM (CycloneDX), cargarlos en Dependency-Track y gestionar VEX para priorizar vulnerabilidades.
- `third-party-risk` (T1) — Usar al incorporar o revisar una dependencia, imagen base o servicio de terceros: criterios de salud, mantenimiento, alternativas y registro de decisión.

## 16-ci-cd (T1) — 13/13

- `alternatives` (T3) — Usar solo si el proyecto no puede usar GitHub Actions: equivalencias y cautelas de GitLab CI y Jenkins respecto a las reglas de CI/CD de la fábrica.
- `contract-gate` (T1) — Usar al integrar Pact en el pipeline: publicar contratos, verificar proveedor y bloquear el despliegue con can-i-deploy.
- `database-migration-step` (T1) — Usar al decidir cómo y cuándo se ejecutan las migraciones de base de datos dentro del pipeline de despliegue.
- `deployment-verification-and-smoke` (T1) — Usar al definir cómo el pipeline verifica un despliegue: readiness, smoke tests, comprobación de versión y criterios para continuar o revertir.
- `ephemeral-preview-environments` (T1) — Usar al crear entornos efímeros por PR (namespace en Kubernetes) para pruebas de integración, contrato y rendimiento, con limpieza y coste acotado.
- `github-actions` (T1) — Usar al escribir o revisar workflows de GitHub Actions: reutilizables, OIDC a la nube, pinning por SHA, runners efímeros, cachés, matrices y environments.
- `performance-gate` (T1) — Usar al añadir pruebas de rendimiento con JMeter al pipeline: umbrales, entorno comparable y detección de regresiones.
- `pipeline-architecture` (T1) — Usar al diseñar el pipeline CI/CD de un proyecto generado: etapas, orden de gates, separación CI/CD y artefactos inmutables.
- `pipeline-observability-and-dora` (T1) — Usar al medir el pipeline: métricas DORA, duración, tasa de fallos y flakiness, y cómo emitirlas sin datos sensibles.
- `quality-gates` (T1) — Usar al definir los gates de calidad bloqueantes del pipeline: tests, cobertura, mutación, arquitectura, estilo y análisis estático.
- `release-versioning-changelog` (T1) — Usar al definir versionado semántico, tags, changelog y notas de release automatizadas desde Conventional Commits.
- `rollback-strategy` (T1) — Usar al diseñar cómo revertir un despliegue desde el pipeline: rollback de aplicación, compatibilidad de esquema, feature flags y roll-forward.
- `security-gates` (T1) — Usar al añadir gates de seguridad al pipeline: SAST, secretos, SCA, escaneo de imagen, IaC, SBOM y firma, con umbrales y excepciones VEX.

## 17-gitops-progressive-delivery (T1) — 9/9

- `argo-cd` (T1) — Usar al definir Applications, ApplicationSets, AppProjects, RBAC, sync waves o notificaciones de Argo CD.
- `argo-rollouts` (T1) — Usar al diseñar despliegues canary o blue-green con Argo Rollouts, incluidos pasos de tráfico y AnalysisTemplates.
- `argo-workflows-and-events` (T1) — Usar al automatizar pipelines por eventos en Kubernetes con Argo Workflows y Argo Events, y al decidir si encajan frente a GitHub Actions.
- `drift-and-self-heal-policy` (T1) — Usar al decidir prune, selfHeal, ignoreDifferences y política de cambios manuales (drift) en Applications de Argo CD por entorno.
- `environment-promotion` (T1) — Usar al promover una versión entre entornos (dev, staging, prod) con GitOps: PRs de promoción, gates y rollback.
- `flux-comparison` (T3) — Usar al comparar Flux con Argo CD o al evaluar migrar; referencia T3, la decisión vigente es Argo CD (D21).
- `repo-strategy` (T1) — Usar al decidir la estructura de repositorios GitOps: código vs manifiestos, mono vs multi-repo, carpetas por entorno y propiedad.
- `secrets-in-gitops` (T1) — Usar al manejar secretos en repos GitOps con Argo CD: qué nunca va a Git y cómo inyectarlos con External Secrets o Vault.
- `spinnaker-comparison` (T3) — Usar al comparar Spinnaker con Argo CD/Rollouts o al heredar pipelines de Spinnaker; referencia T3 (D21 fija Argo).

## 18-observability-platform (T1) — 10/10

- `alert-routing-and-oncall` (T1) — Usar al escribir reglas de alerta de Prometheus y configurar Alertmanager: severidades, agrupación, inhibición y guardia.
- `cardinality-and-cost-governance` (T1) — Usar al añadir métricas, etiquetas o logs nuevos, o al investigar crecimiento de series y coste de observabilidad.
- `collector-pipelines` (T1) — Usar al definir o revisar pipelines del OpenTelemetry Collector (receivers, processors, exporters) que alimentan Prometheus, Loki y Tempo.
- `dashboards-and-slos-as-code` (T1) — Usar al crear dashboards de Grafana y SLOs: versionados como código, provisionados y con reglas de burn rate generadas.
- `logs-and-traces-stores` (T1) — Usar al configurar Loki (logs) y Tempo (trazas): almacenamiento en objeto, retención, etiquetas e indexado.
- `metrics-store-ha-retention` (T1) — Usar al dimensionar Prometheus: alta disponibilidad, retención local y almacenamiento a largo plazo vía remote write.
- `multi-tenant-observability` (T1) — Usar al aislar la telemetría por equipo o entorno en Loki, Tempo, Prometheus y Grafana (tenants, cabeceras, límites por tenant).
- `observability-of-the-platform-itself` (T1) — Usar al monitorizar la propia plataforma de observabilidad (Prometheus, Collector, Loki, Tempo, Grafana, Alertmanager) y evitar puntos ciegos.
- `status-page-and-comms` (T1) — Usar al definir la página de estado y la comunicación de incidentes a usuarios y stakeholders durante degradaciones o caídas.
- `tempo-and-service-graphs` (T1) — Usar al habilitar el metrics-generator de Tempo (service graphs, span metrics) y al enlazar trazas con métricas y logs en Grafana.

## 19-resilience-dr-finops (T1) — 20/20

- `application-recovery-controller-and-health-checks` (T1) — Usar al diseñar la conmutación de tráfico entre regiones o AZ: routing controls y zonal shift de ARC, health checks de Route 53 y qué evitar en el plano de control.
- `backup-vault-immutability-and-restore-tests` (T1) — Usar al diseñar backups inmutables (AWS Backup Vault Lock, copia cross-region/cuenta) y pruebas periódicas de restauración; cubre corrupción y ransomware que la replicación no resuelve.
- `capacity-and-load-modeling` (T1) — Usar al dimensionar capacidad, modelar carga o planificar pruebas de carga y headroom, incluido el pico que provoca un failover regional.
- `change-and-release-management` (T1) — Usar al diseñar el proceso de cambios y despliegues seguros: canary por celda/región, ventanas, rollback, congelaciones y vínculo con el presupuesto de error.
- `data-replication-matrix` (T1) — Usar al decidir cómo se replica cada almacén entre eu-west-1 y eu-central-1 (Aurora, DynamoDB, MSK, S3, caché, secretos) y qué RPO real ofrece cada uno.
- `dependency-mapping-and-blast-radius` (T1) — Usar al mapear dependencias de un servicio y estimar su radio de impacto antes de fijar tiers, DR o cambios; incluye dependencias duras, blandas y ocultas.
- `eks-multi-region-and-argo-cd-multicluster` (T1) — Usar al diseñar EKS en varias regiones y su entrega GitOps con Argo CD multicluster: topología, ApplicationSets, estado y fallo del plano de control.
- `failover-and-failback-runbooks` (T1) — Usar al escribir o revisar el runbook de failover/failback eu-west-1 a eu-central-1: orden de pasos, Aurora Global antes que Vault, decisión de conmutar y vuelta atrás.
- `fault-injection-and-game-days` (T1) — Usar al planificar ejercicios de resiliencia: game days tabletop, inyección de fallos (Chaos Mesh, Toxiproxy, Chaos Monkey) y experimentos AWS FIS solo como diseño.
- `finops` (T1) — Usar al definir presupuestos, alertas de anomalías, etiquetado, rightsizing y coste unitario de un proyecto en AWS (diseño; sin cuenta real).
- `finops-of-resilience` (T1) — Usar al presupuestar o comparar estrategias de resiliencia/DR (multi-AZ, warm standby, activo-activo): coste por tier, transferencia entre regiones y coste de la indisponibilidad.
- `incident-management-and-postmortems` (T1) — Usar al definir cómo se declara, gestiona y revisa un incidente operativo: roles, severidades, comunicación y postmortem sin culpas con acciones medibles.
- `istio-multicluster-tradeoffs` (T1) — Usar al decidir si extender Istio a varios clústeres/regiones: multi-primary vs primary-remote, redes, failover por localidad y coste operativo.
- `load-shedding-and-degradation` (T1) — Usar al diseñar cómo un servicio rechaza o degrada carga bajo saturación o fallo parcial: prioridades, límites de concurrencia, modos degradados y retrocesos.
- `multi-az-patterns` (T1) — Usar al diseñar o revisar alta disponibilidad dentro de una región AWS: nodos EKS en 3 AZ, topology spread, PDB y datos Multi-AZ (Aurora, MSK, Vault Raft).
- `multi-region-patterns` (T1) — Usar al diseñar la región secundaria (eu-central-1) de un servicio: warm standby, clúster gemelo, Vault por región, ECR replicado y dependencias que no deben cruzar regiones.
- `resilience-hub-assessments` (T2) — Usar al preparar una evaluación de resiliencia con AWS Resilience Hub: política RTO/RPO por tier, recomendaciones y cómo tratarlas como diseño, no como prueba.
- `slo-error-budget-policy` (T1) — Usar al definir SLIs/SLOs y la política de presupuesto de error que decide cuándo congelar cambios y priorizar fiabilidad.
- `static-stability-and-cell-architecture` (T1) — Usar al decidir cuánta capacidad pre-aprovisionar en la secundaria y cómo limitar el radio de impacto con celdas o shards; evita depender de operaciones de control durante el fallo.
- `tier-model-and-rpo-rto` (T1) — Usar al declarar o revisar el tier de resiliencia (0-3) y los objetivos RPO/RTO de un proyecto, antes de diseñar multi-AZ, multi-región o backups.

## 20-internal-developer-platform (T2) — 5/5

- `backstage` (T2) — Usar al montar o mantener un portal de desarrollador con Backstage: catalog-info.yaml, propiedad de componentes, scorecards y TechDocs.
- `developer-experience-metrics` (T2) — Usar al definir métricas de experiencia de desarrollo y entrega (DORA, tiempo de onboarding, encuestas) sin convertirlas en vigilancia individual.
- `ephemeral-environments` (T2) — Usar al diseñar entornos efímeros por pull request (namespace temporal, datos sintéticos, destrucción automática) en Kubernetes.
- `golden-paths-governance` (T2) — Usar al definir, versionar o retirar golden paths (caminos pavimentados) de la plataforma interna y decidir cuándo una desviación está permitida.
- `software-templates` (T2) — Usar al diseñar plantillas de scaffolding (Backstage Scaffolder) que crean servicios nuevos con estándares, CI y catálogo ya incluidos.

## 21-on-prem-hybrid (T3) — 4/4

- `hybrid-identity-and-networking` (T3) — Usar al conectar entornos on-prem con la nube: federación de identidad (OIDC/Keycloak), VPN o enlace dedicado, DNS y direccionamiento sin solapes.
- `kubernetes-on-prem` (T3) — Usar al diseñar un clúster Kubernetes propio (on-prem o híbrido) con kubeadm: topología HA, etcd, actualizaciones y respaldos.
- `private-registry` (T3) — Usar al montar un registro privado de imágenes (Harbor) on-prem: proyectos, replicación, escaneo, caché proxy y firma.
- `storage-and-load-balancing` (T3) — Usar al elegir almacenamiento persistente (CSI) y balanceo de carga (LoadBalancer, ingress) en clústeres Kubernetes on-prem sin servicios del proveedor cloud.

## 22-polyglot-persistence (T1) — 21/21

- `aggregates-and-event-design` (T1) — Usar al diseñar agregados y eventos de un sistema con event sourcing: límites del stream, nombres, contenido, metadatos y comandos; subskill de event-sourcing.
- `audit-trail-without-event-sourcing` (T1) — Usar cuando se necesita historial de cambios o auditoría de negocio y se duda entre event sourcing y alternativas más simples (tabla de auditoría, Envers, CDC, temporal tables).
- `cache-strategies` (T1) — Usar al introducir Redis como caché (cache-aside, TTL, invalidación, evicción, stampede) delante de Postgres o DynamoDB.
- `consistency-and-sagas` (T1) — Usar al coordinar cambios que abarcan varios datastores o servicios (Postgres, DynamoDB, mensajería) y hay que elegir transacción local, saga o compensación.
- `cqrs-read-models-and-search` (T1) — Usar al construir un read model o índice de búsqueda (OpenSearch) derivado de la base de datos de escritura, con consistencia eventual y sin doble escritura.
- `data-sync-pitfalls` (T1) — Usar al sincronizar datos entre datastores (SQL, DynamoDB, OpenSearch, Redis) por eventos, CDC o jobs, para evitar divergencias, pérdidas, duplicados y desorden.
- `datastore-selection-guide` (T1) — Usar al elegir el almacén de datos de un agregado o caso de uso (Postgres, DynamoDB, OpenSearch, Redis) y al decidir si hace falta persistencia políglota.
- `dynamodb-data-modeling` (T1) — Usar al diseñar tablas, claves e índices de DynamoDB a partir de patrones de acceso (single-table vs multi-table, GSI, hot partitions).
- `dynamodb-event-store` (T1) — Usar al implementar un event store sobre DynamoDB: esquema de streams, append condicional, publicación desde DynamoDB Streams y límites.
- `event-versioning-and-upcasting` (T1) — Usar al cambiar la forma de un evento almacenado: versionado de esquema, upcasters, cambios compatibles y qué no hacer con eventos inmutables; subskill de event-sourcing.
- `gdpr-and-immutable-events` (T1) — Usar al diseñar eventos inmutables (event sourcing, logs, outbox) que contienen datos personales y hay que atender supresión o rectificación.
- `global-tables-and-write-region-rules` (T1) — Usar al replicar DynamoDB entre regiones (Global Tables): modo de consistencia, conflictos last-writer-wins y región de escritura por agregado o tenant.
- `local-vs-aws-dynamodb-testing` (T1) — Usar al probar código DynamoDB con DynamoDB Local o Testcontainers: qué cubre el emulador, qué NO reproduce y cómo declarar ese límite.
- `mongodb-alternative` (T3) — Usar solo si se propone MongoDB (o compatible) en lugar de DynamoDB como almacén documental; referencia T3 con criterios y límites.
- `outbox-and-cdc` (T1) — Usar al publicar eventos tras un cambio en la base de datos sin doble escritura: patrón transactional outbox, relay por polling o CDC (Debezium, DynamoDB Streams).
- `polyglot-operations-cost` (T1) — Usar antes de añadir un almacén (DynamoDB, OpenSearch, Redis) a un proyecto, para estimar y aceptar su coste operativo y de equipo.
- `projections-and-read-models` (T1) — Usar al construir proyecciones o read models (Postgres, OpenSearch) a partir de eventos: idempotencia, orden, checkpoints y consistencia eventual; subskill de event-sourcing.
- `rebuilds-and-replays` (T1) — Usar al reconstruir proyecciones o read models de un sistema event-sourced desde el log de eventos (rebuild, replay, blue/green de proyecciones).
- `snapshots` (T1) — Usar cuando reconstruir un agregado event-sourced desde sus eventos es lento y se plantean snapshots; subskill de event-sourcing.
- `testing-event-sourced-systems` (T1) — Usar al escribir tests de aggregates, upcasters y proyecciones en sistemas event-sourced (given-when-then sobre eventos, replay, concurrencia).
- `when-to-use-and-when-not` (T1) — Usar para decidir si un agregado necesita event sourcing, outbox o solo un audit trail; subskill de event-sourcing con árbol de decisión.

## 23-data-platform (T2) — 15/15

- `access-control-masking-and-retention` (T2) — Usar al definir quién lee qué en el lago o warehouse: roles, enmascarado de columnas, seguridad por fila y políticas de retención/borrado de datasets.
- `batch-orchestration` (T2) — Usar al diseñar pipelines batch orquestados con Airflow o Dagster: DAGs idempotentes, reintentos, backfills, particiones por intervalo, alertas y secretos.
- `bi-and-reporting` (T2) — Usar al elegir herramienta BI, diseñar capa semántica, dashboards y reportes sobre el warehouse, incluyendo permisos, rendimiento y definiciones únicas de métricas.
- `cdc-and-streaming` (T2) — Usar al alimentar la plataforma de datos desde BD transaccionales con CDC (Debezium/Kafka Connect) o streaming: slots, snapshots, orden, esquemas y reprocesado.
- `data-contracts-and-lineage` (T2) — Usar al acordar el esquema y SLAs de un dataset entre productor y consumidores (data contract) y al capturar linaje con OpenLineage/Marquez.
- `data-governance-and-classification` (T2) — Usar al definir dueños, catálogo, niveles de clasificación y etiquetas de datos en una plataforma analítica (lago, warehouse, marts) antes de abrir acceso a consumidores.
- `data-lake-and-lakehouse` (T2) — Usar al diseñar un data lake o lakehouse: zonas raw/curated, formatos de tabla abiertos (Iceberg/Delta/Parquet), particionado, compactación, catálogo y evolución de esquema.
- `data-modeling` (T2) — Usar al modelar tablas analíticas: esquema en estrella (hechos y dimensiones), granularidad, claves surrogate, SCD tipo 2, medidas aditivas y alternativas como Data Vault u OBT.
- `data-observability` (T2) — Usar al monitorizar pipelines y datasets en producción: frescura, volumen, esquema, distribución, linaje y alertas con SLO, para detectar datos rotos antes que el negocio.
- `data-platform-cost` (T2) — Usar al dimensionar o revisar el coste de una plataforma de datos: almacenamiento, cómputo de consultas, ingesta, egress, particionado y formatos, con presupuestos y atribución por dominio.
- `data-quality` (T2) — Usar al definir o revisar controles de calidad de datos en pipelines: dimensiones de calidad, tests dbt/Great Expectations, umbrales, cuarentena y qué hacer cuando fallan.
- `etl-vs-elt-and-dbt` (T2) — Usar al elegir entre ETL y ELT y al modelar transformaciones SQL con dbt: capas staging/intermediate/marts, materializaciones incrementales, tests y documentación.
- `feature-store-and-ml-data` (T2) — Usar al preparar datos de entrenamiento y features para ML: feature store, joins point-in-time, consistencia offline/online, versionado de datasets y datos personales.
- `gdpr-in-the-lake` (T2) — Usar al diseñar borrado, rectificación, minimización y bases legales sobre datos personales en lago/warehouse (formatos append-only, backups, copias derivadas). Borrador legal.
- `warehouse-options` (T2) — Usar al elegir el motor analítico/warehouse (PostgreSQL, ClickHouse, DuckDB, Trino, Redshift, Athena...) según volumen, concurrencia, latencia, coste y licencia.

## 24-ai-engineering (T2) — 21/21

- `agents-and-tool-calling` (T2) — Usar al dar herramientas a un LLM o construir un agente en Java: diseño de tools, permisos mínimos, límites de bucle, idempotencia y confirmación humana de acciones.
- `ai-safety-and-red-teaming` (T2) — Usar al planificar pruebas adversarias (red teaming) de un sistema con LLM propio: alcance escrito, categorías de riesgo, casos de prueba, severidad y remediación.
- `chatbot-design` (T2) — Usar al diseñar un chatbot o asistente conversacional corporativo: alcance, memoria, escalado a humano, transparencia y manejo de fallos.
- `classical-mlops` (T2) — Usar al llevar un modelo de ML clásico (scikit-learn, XGBoost, series temporales) a un servicio: reproducibilidad, registro de modelos, validación, despliegue y monitorización de deriva.
- `document-management` (T2) — Usar al diseñar el almacenamiento de documentos de usuario (PDF, contratos, adjuntos): objeto en S3 más metadatos en BD, versionado, retención, hash y control de acceso.
- `guardrails-and-pii-redaction` (T2) — Usar al proteger entradas y salidas de un LLM: redacción de PII antes de enviar o registrar, filtros de contenido, validación de salida y comportamiento ante bloqueo.
- `human-in-the-loop` (T2) — Usar al diseñar flujos donde un LLM o agente propone acciones o decisiones que una persona debe aprobar, corregir o revisar antes de que tengan efecto.
- `intelligent-document-processing` (T2) — Usar al diseñar un pipeline de procesamiento inteligente de documentos: ingesta, OCR, clasificación, extracción y revisión humana de facturas, contratos o formularios.
- `llm-evals` (T2) — Usar al añadir o cambiar un prompt, modelo, RAG o agente: define datasets de evaluación, métricas, jueces LLM y umbrales que bloquean regresiones en CI.
- `llm-gateway` (T2) — Usar al decidir cómo acceden los servicios a proveedores LLM: pasarela central vs cliente directo, enrutado de modelos, claves, cuotas, caché, fallback y auditoría.
- `mcp-servers-in-java` (T2) — Usar al exponer capacidades propias como servidor MCP (Model Context Protocol) en Java/Spring Boot: transporte, autenticación, herramientas mínimas y seguridad.
- `model-risk-and-ai-act-mapping` (T2) — Usar al clasificar un sistema de IA por riesgo, mapearlo al Reglamento UE de IA (AI Act) y documentar riesgos de modelo; borrador por confirmar legalmente.
- `ocr-options` (T2) — Usar al elegir el motor OCR de un pipeline de documentos: Tesseract local frente a servicios gestionados o modelos de visión, con criterios de calidad, coste y privacidad.
- `prompt-management` (T2) — Usar al escribir, versionar o desplegar prompts de LLM en un servicio: plantillas, versionado, revisión, pruebas de regresión y separación de datos no confiables.
- `rag-architecture` (T2) — Usar al diseñar un sistema RAG (ingesta, chunking, embeddings, recuperación, reranking, generación con citas): decisiones de arquitectura y fallos típicos.
- `rag-over-enterprise-docs` (T2) — Usar al montar RAG sobre documentos corporativos (PDF, Office, wikis): conectores, parsing, permisos heredados, frescura, borrado y datos personales.
- `spring-ai-and-langchain4j` (T2) — Usar al elegir o integrar un framework LLM en Java/Spring Boot (Spring AI o LangChain4j): criterios de elección, abstracciones, aislamiento del proveedor y pruebas.
- `structured-outputs-and-streaming` (T2) — Usar cuando una respuesta de LLM alimenta código (JSON/esquema) o se envía al cliente en streaming (SSE): esquemas, validación, reintentos y cancelación.
- `token-and-cost-budgets` (T2) — Usar al integrar un LLM en un servicio: límites de tokens, presupuesto de coste por petición/tenant, caché, enrutado de modelos y alertas de gasto.
- `training-data-licensing-and-provenance` (T2) — Usar al reunir datos o documentos para entrenar, afinar o alimentar un RAG: licencias, base legal, procedencia, consentimiento y registro de origen.
- `vector-store-selection` (T2) — Usar al elegir dónde guardar embeddings para búsqueda semántica o RAG: pgvector, OpenSearch u otros, con criterios de escala, filtrado, consistencia y coste.

## 25-security-operations (T2) — 16/16

- `bug-bounty-and-disclosure` (T2) — Usar al definir política de divulgación de vulnerabilidades (security.txt, VDP) o un programa de bug bounty, incluyendo triaje, safe harbor y plazos.
- `cspm-and-posture` (T2) — Usar al montar o revisar la vigilancia de postura de seguridad cloud y Kubernetes (CSPM) con herramientas abiertas como Prowler y Kubescape, y su gestión de hallazgos.
- `dast-and-attack-simulation` (T2) — Usar al integrar DAST (OWASP ZAP) o simulación de ataques en CI o staging propios, con alcance acotado y autorizado; nunca contra terceros.
- `encryption-standards` (T2) — Usar al elegir algoritmos, longitudes de clave, TLS y cifrado en reposo; define el estándar de cifrado y la migración a criptografía post-cuántica.
- `hardening-baselines` (T2) — Usar al definir o revisar líneas base de endurecimiento (CIS Benchmarks) para imágenes, nodos, clústeres y servicios, con desviaciones documentadas.
- `iam-governance-and-pam` (T2) — Usar al diseñar o revisar el gobierno de identidades: ciclo joiner-mover-leaver, recertificación de accesos, cuentas privilegiadas (PAM) y separación de funciones.
- `ids-ips-waf-edr` (T2) — Usar al elegir y desplegar controles de detección y bloqueo: IDS/IPS de red, WAF, EDR y detección en runtime de contenedores, y cómo se ajustan sin romper tráfico legítimo.
- `incident-response-playbooks-and-forensics` (T2) — Usar al escribir playbooks de respuesta a incidentes de seguridad y al definir preservación de evidencia y cadena de custodia forense.
- `penetration-testing-program` (T2) — Usar al planificar o revisar pruebas de penetración sobre sistemas propios: alcance y reglas de compromiso por escrito, metodología, informe y seguimiento.
- `pki-and-certificate-lifecycle` (T2) — Usar al diseñar la PKI interna o el ciclo de vida de certificados TLS (emisión, renovación automática, revocación, inventario) con cert-manager u otra CA.
- `ransomware-resilience` (T2) — Usar al diseñar defensas y recuperación frente a ransomware: copias inmutables aisladas, segmentación, privilegios mínimos y pruebas de restauración.
- `security-champions-and-training` (T2) — Usar al montar un programa de security champions y formación de seguridad para equipos de desarrollo, con roles, cadencia y métricas útiles.
- `siem-and-detection-engineering` (T2) — Usar al diseñar la recogida de logs de seguridad, un SIEM (p. ej. Wazuh) o reglas de detección como código con pruebas y ajuste de falsos positivos.
- `third-party-and-supply-chain-risk` (T2) — Usar al evaluar proveedores y componentes externos como riesgo de negocio: due diligence, cláusulas contractuales, monitorización continua y plan de salida.
- `threat-intel-and-risk-register` (T2) — Usar al incorporar inteligencia de amenazas (CISA KEV, avisos de proveedores) y al mantener el registro de riesgos de seguridad con propietarios, tratamiento y revisión.
- `vulnerability-management-program` (T2) — Usar al definir o revisar el programa de gestión de vulnerabilidades: inventario, priorización, SLAs de remediación, excepciones y métricas.

## 26-enterprise-capabilities (T2) — 16/16

- `api-productization-and-developer-portal` (T2) — Usar al convertir una API en producto para terceros: claves y planes, portal de desarrolladores, sandbox, documentación, SDKs, cuotas, versionado y soporte.
- `audit-trail-and-activity-log` (T2) — Usar al diseñar el registro de auditoria de negocio (quien hizo que y cuando) y el historial de actividad visible al usuario en una aplicacion empresarial.
- `back-office-admin-console` (T2) — Usar al diseñar o revisar una consola de administración / back-office (soporte, operaciones, impersonación, acciones masivas) con permisos, auditoría y aprobación de acciones sensibles.
- `consent-and-dsar-management` (T2) — Usar al implementar registro de consentimientos, preferencias y solicitudes de derechos de interesados (acceso, rectificación, supresión, portabilidad) con plazos y trazabilidad. Borrador legal.
- `document-and-report-generation` (T2) — Usar al generar PDF, Excel/CSV o informes desde el backend: plantillas, asincronía, almacenamiento, límites de memoria y datos sensibles.
- `i18n-and-localization` (T2) — Usar al preparar el backend para varios idiomas y regiones: mensajes, locale, zonas horarias, formatos, moneda y contenido traducible almacenado. Complementa frontend-i18n-and-formatting.
- `identity-and-customer-management` (T2) — Usar al diseñar identidad de usuarios/clientes (registro, perfil, federación, roles) sobre Keycloak y su separación del modelo de cliente de negocio.
- `import-export-and-bulk-data` (T2) — Usar al implementar importación/exportación masiva (CSV/Excel/JSON) por usuarios o integraciones: validación, staging, errores por fila e idempotencia.
- `integrations-erp-crm` (T2) — Usar al integrar con ERP o CRM externos (SAP, Odoo, Salesforce, HubSpot u otros): sincronización, mapeo, idempotencia, límites de API, conciliación y fallos del sistema externo.
- `multi-tenancy-saas-features` (T2) — Usar al construir funciones SaaS multi-tenant sobre el modelo ya elegido: onboarding de tenants, planes y límites, configuración por tenant, dominios propios y offboarding.
- `notifications` (T2) — Usar al diseñar envío de notificaciones (email, SMS, push, in-app): plantillas, preferencias, reintentos, idempotencia y proveedores.
- `payments-and-billing` (T2) — Usar al integrar pasarelas de pago, modelar importes, cobros recurrentes, facturacion o conciliacion; cubre dinero, idempotencia y webhooks.
- `rules-engines` (T2) — Usar al decidir si reglas de negocio cambiantes (precios, elegibilidad, scoring) van en código, tablas de decisión o un motor de reglas (Drools/DMN).
- `scheduling-and-batch-jobs` (T2) — Usar al crear tareas programadas o jobs batch (Spring @Scheduled, ShedLock, Quartz, Spring Batch) en servicios con varias réplicas.
- `search-and-discovery` (T2) — Usar al añadir búsqueda de texto, filtros/facetas o autocompletado: PostgreSQL FTS vs OpenSearch, indexación derivada y consistencia.
- `workflow-bpm` (T2) — Usar al introducir procesos de larga duración, aprobaciones humanas o BPMN (Camunda/Flowable) en lugar de máquinas de estado ad hoc.

## 27-frontend-react (T1) — 23/23

- `accessibility` (T1) — Usar al construir o revisar componentes, formularios y flujos React para cumplir WCAG 2.2 AA: semántica, teclado, foco, contraste y pruebas con axe.
- `api-client-from-openapi` (T1) — Usar al consumir una API desde React: generar tipos/cliente desde el OpenAPI del backend, regenerar en CI y no escribir llamadas HTTP a mano.
- `auth-and-session` (T1) — Usar al implementar login, sesión y rutas protegidas en React: OIDC con PKCE, patrón BFF con cookie de sesión, sin tokens en localStorage.
- `build-and-deploy` (T1) — Usar al configurar el build con pnpm/Vite y el despliegue estático de la SPA (S3 + CloudFront): caché, invalidación, fallback SPA y multi-región.
- `component-patterns` (T1) — Usar al diseñar o revisar componentes y hooks React: composición, compound components, hooks propios, render props y cuándo memoizar.
- `design-system-and-tokens` (T1) — Usar al crear o mantener el sistema de diseño: tokens (color, espaciado, tipografía), componentes base documentados en Storybook y temas.
- `error-handling-and-boundaries` (T1) — Usar al gestionar errores en React: error boundaries por zona, errores de red/Problem Details, estados de fallo en UI y reporte sin datos sensibles.
- `feature-flags-ui` (T1) — Usar al condicionar UI o rutas React con feature flags (OpenFeature): evaluación, carga inicial, flicker, limpieza y por qué un flag no protege.
- `forms-and-validation` (T1) — Usar al construir formularios React: React Hook Form con esquemas Zod, mensajes de error accesibles, errores del servidor y envío seguro.
- `frontend-architecture` (T1) — Usar al estructurar un proyecto React: carpetas por feature, límites entre módulos, API pública de cada feature y dirección de dependencias.
- `frontend-i18n-and-formatting` (T1) — Usar al añadir textos, fechas, números, monedas o idiomas a la UI React: catálogos de mensajes, formato con Intl y RTL.
- `frontend-performance` (T1) — Usar al optimizar o revisar rendimiento de la SPA React: Core Web Vitals, presupuestos de bundle, imágenes, renders y medición.
- `micro-frontends` (T3) — Usar solo si se plantea dividir el frontend en micro-frontends (Module Federation u otros): cuándo no hacerlo, contratos, dependencias compartidas y gobierno.
- `observability-frontend` (T1) — Usar al instrumentar la SPA con OpenTelemetry del navegador, RUM, Web Vitals y reporte de errores, correlacionando con trazas del backend.
- `pwa-and-offline` (T3) — Usar solo si la SPA necesita instalarse o funcionar sin conexión (PWA, service worker): estrategias de caché, actualizaciones, datos sensibles y cola de escrituras.
- `realtime` (T1) — Usar al añadir actualizaciones en tiempo real a la SPA con SSE o WebSocket: elección, autenticación, reconexión, integración con TanStack Query y límites.
- `rendering-strategy-decision` (T1) — Usar al decidir cómo renderiza una app React: SPA con Vite (defecto, ADR-0036) frente a SSR/Next.js, y qué evidencia justifica cambiar.
- `routing-and-code-splitting` (T1) — Usar al definir rutas en React Router, guards de navegación y carga diferida (lazy) de rutas para dividir el bundle.
- `security-frontend` (T1) — Usar al escribir o revisar código React que renderiza HTML, carga scripts, define CSP/cabeceras o maneja datos sensibles en el navegador (XSS).
- `state-management` (T1) — Usar al decidir dónde vive el estado en React: server-state (TanStack Query), client-state (Zustand/Redux Toolkit), URL y formularios.
- `supply-chain-npm` (T1) — Usar al añadir, actualizar o auditar dependencias npm/pnpm del frontend: lockfile, scripts de instalación, typosquatting, auditoría y SBOM.
- `testing` (T1) — Usar al escribir o revisar tests del frontend React: Vitest, Testing Library, MSW, Playwright, regresión visual y accesibilidad.
- `typescript-strict-rules` (T1) — Usar al configurar tsconfig/ESLint o escribir tipos en TypeScript/React: modo strict, sin any, validación en los bordes y uniones discriminadas.

## 28-local-kubernetes (T1) — 9/9

- `aws-emulation` (T1) — Usar al decidir cómo emular servicios AWS en local (DynamoDB Local, MinIO, LocalStack) y al documentar sus límites; no sustituye a AWS.
- `cluster-tooling` (T1) — Usar al crear o documentar el Kubernetes local de un proyecto: kind por defecto (ADR-0034), k3d alternativa, registro local y config reproducible.
- `data-seeding-and-demo-data` (T1) — Usar al cargar datos de demo o de desarrollo en el clúster local: seeds idempotentes, sintéticos y sin PII, aplicados por Job de Kubernetes.
- `dev-loop` (T1) — Usar al configurar el bucle de desarrollo inner-loop en Kubernetes local con Tilt o Skaffold: rebuild, sync, port-forward y límites del hot reload en Java.
- `devcontainer-integration` (T1) — Usar al preparar un devcontainer que traiga kind, kubectl, Helm, Tilt y el resto del tooling local para que el clúster arranque igual en cualquier máquina.
- `local-gitops` (T1) — Usar al probar GitOps con Argo CD en el clúster local (opcional): app-of-apps contra un repositorio git local, sin tocar entornos reales.
- `local-parity-matrix` (T1) — Usar al documentar o revisar la equivalencia AWS-local de un proyecto y lo que el Kubernetes local no reproduce; fuente: catalog/parity-matrix.yaml.
- `local-profiles` (T1) — Usar al definir qué se levanta en local: perfil mínimo (servicio + Postgres + DynamoDB Local) y completo (Kafka, Vault, Istio, observabilidad).
- `resource-budgets` (T1) — Usar al fijar CPU/RAM del clúster local y los requests/limits por perfil (minimal/full), para que el portátil del desarrollador aguante.

## 29-cloud-readiness (T1) — 6/6

- `cost-estimation` (T1) — Usar al estimar el coste de la infraestructura AWS diseñada (Infracost o equivalente) sin desplegar; incluye el sobrecoste por tier de resiliencia.
- `dr-tabletop-exercises` (T1) — Usar al planificar o documentar un simulacro de DR sobre papel (tabletop): escenarios, tiers RPO/RTO, roles y registro; sustituye lo que local no puede probar.
- `honest-claims-policy` (T1) — Usar al redactar cualquier texto sobre AWS, infraestructura o madurez: qué se puede afirmar y qué no, con la fórmula obligatoria de honestidad.
- `maturity-labels` (T1) — Usar al escribir un README, informe o ADR sobre infraestructura: qué etiqueta de madurez poner (validada estáticamente, no verificada en real) y dónde.
- `parity-matrix-maintenance` (T1) — Usar al añadir, cambiar o retirar un servicio AWS o su equivalente local y mantener catalog/parity-matrix.yaml coherente con los skills afectados.
- `static-verification-ladder` (T1) — Usar al verificar Terraform/IaC sin desplegar: validate, tflint, Checkov/Trivy, OPA sobre HCL o plan, mock providers. Define el techo de madurez.

## 30-engineering-process (T1) — 19/19

- `adr` (T1) — Usar al tomar, cambiar o revertir una decisión arquitectónica: cómo redactar, numerar, versionar y sustituir Architecture Decision Records en catalog/adr o docs/adr.
- `api-docs` (T1) — Usar al documentar APIs REST o de eventos de un proyecto: OpenAPI/AsyncAPI como fuente única, ejemplos, errores y portal de consumo.
- `c4-and-arc42` (T1) — Usar al documentar la arquitectura de un proyecto: diagramas C4 (contexto, contenedores, componentes) y estructura arc42 para la documentación completa.
- `changelog-release-notes` (T1) — Usar al redactar el CHANGELOG y las notas de release de un proyecto: formato, audiencia, cambios incompatibles y avisos de migración.
- `conventional-commits` (T1) — Usar al redactar mensajes de commit o títulos de PR/squash, o al configurar la validación de commits y la generación automática de changelog.
- `definition-of-ready-and-done` (T1) — Usar al planificar o cerrar una historia/tarea: criterios para empezar (Definition of Ready) y para darla por terminada (Definition of Done) con evidencia.
- `diagrams-as-code` (T1) — Usar al crear o actualizar diagramas de arquitectura, secuencia o flujo: definirlos como texto versionado (Mermaid, PlantUML, Structurizr DSL) revisable en PR.
- `domain-discovery` (T1) — Usar al arrancar un dominio nuevo o poco claro: sesiones de event storming para descubrir eventos, agregados, contextos delimitados y lenguaje ubicuo.
- `git-workflow` (T1) — Usar al crear ramas, integrar cambios o decidir cómo versionar trabajo en un proyecto generado: trunk-based development con ramas cortas y feature flags.
- `lessons-learned-and-retro` (T1) — Usar tras un incidente, hito o iteración para hacer retrospectivas y postmortems sin culpables, con acciones con dueño y seguimiento.
- `library-selection-and-tech-radar-process` (T1) — Usar al incorporar, sustituir o retirar una librería o tecnología: criterios de selección, licencia, ADR y mantenimiento de un radar tecnológico.
- `living-readme` (T1) — Usar al crear o actualizar el README de un proyecto generado o un módulo, para que siga siendo verdadero, ejecutable y corto.
- `pr-rules` (T1) — Usar al abrir, describir o revisar un pull request: tamaño, plantilla de descripción, checks requeridos, aprobaciones y cuándo no se puede hacer merge.
- `production-readiness-review` (T1) — Usar antes de dar un servicio por apto para operar (PRR): checklist de observabilidad, resiliencia, seguridad, datos y operación, con honestidad sobre AWS.
- `requirements-engineering` (T1) — Usar al redactar o refinar historias, criterios de aceptación y requisitos no funcionales: INVEST, Gherkin y NFR medibles antes de implementar.
- `rfc-process` (T1) — Usar cuando un cambio amplio o controvertido necesita debate escrito y consenso antes de decidir (impacto en varios equipos): proceso RFC previo al ADR.
- `risk-register` (T1) — Usar al identificar, puntuar y dar seguimiento a riesgos de proyecto o técnicos: registro versionado con dueño, mitigación y revisión periódica.
- `runbooks` (T1) — Usar al escribir o revisar runbooks operativos: estructura, verificación, pasos seguros y enlace desde alertas.
- `tech-debt-register` (T1) — Usar al registrar, priorizar y pagar deuda técnica: entradas con coste, interés, dueño y fecha, enlazadas a TODOs del código.

## 31-agentic-engineering (T1) — 13/13

- `agent-evals` (T1) — Usar al diseñar o ejecutar evaluaciones que comprueben que los agentes y hooks respetan reglas y gates (tests/agent-evals, tests/hooks).
- `bootstrap-generated-project-claude-config` (T1) — Usar en /project-init para crear el .claude/, CLAUDE.md y hooks de un proyecto generado a partir de las guías de la fábrica (sin plantillas).
- `claude-md-authoring` (T1) — Usar al escribir o editar un CLAUDE.md (de la fábrica o de un proyecto generado) para que sea corto y efectivo.
- `context-budgeting` (T1) — Usar cuando una sesión se alarga, el contexto se llena o al decidir qué cargar (CLAUDE.md, skills, MCP, ficheros): presupuesto de contexto y compactación.
- `cost-control` (T1) — Usar al planificar sesiones largas, subagentes en paralelo o cargas masivas de contexto para acotar el consumo de tokens y el coste del uso de agentes.
- `gate-protocol` (T1) — Usar al terminar una fase del flujo o antes de avanzar de gate; define cómo parar, pedir aprobación humana y registrarla.
- `handoff-artifacts-between-agents` (T1) — Usar cuando un agente entrega trabajo a otro (analista a arquitecto, tech-lead a ingeniería) para definir qué artefacto, formato y evidencias se pasan.
- `mcp-governance` (T1) — Usar al añadir, aprobar o revisar servidores MCP (.mcp.json, permisos mcp__*) en la fábrica o en un proyecto generado.
- `parallel-work-and-worktrees` (T1) — Usar al repartir trabajo entre varias sesiones o agentes a la vez, para aislar ediciones con git worktree y evitar colisiones y merges rotos.
- `prompt-injection-defense-for-agents` (T1) — Usar cuando un agente lee webs, ficheros, resultados de herramientas o MCP no confiables, o al revisar permisos de agentes expuestos a contenido externo.
- `skill-authoring-guide` (T1) — Usar al crear o revisar un skill de la fábrica; define anatomía obligatoria, niveles T1/T2/T3 y reglas de enforcement.
- `subagent-design` (T1) — Usar al crear o revisar un subagente en .claude/agents/ o al decidir si delegar una tarea: alcance, herramientas mínimas, modelo y contrato de salida.
- `verify-before-asserting` (T1) — Usar antes de afirmar versiones, comportamiento de herramientas, normativa o que algo funciona; obliga a verificar o marcar TODO-VERIFY.
