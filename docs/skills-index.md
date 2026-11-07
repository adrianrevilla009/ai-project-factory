# Índice de skills

> Generado por `factory/tools/build_index.py`. No editar a mano.

Skills: **327** de 487 previstos en `catalog/skills-inventory.yaml`.

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

## 12-aws-networking (T1) — 3/11

- `cidr-planning-and-ipam` (T1) — Usar al diseñar rangos CIDR de VPC, subredes o EKS, o al introducir VPCs nuevas que deban conectarse por TGW, peering o VPN sin solapamientos.
- `transit-gateway-hub-and-spoke` (T1) — Usar al conectar varias VPC o cuentas con Transit Gateway: tablas de rutas segmentadas, inspección centralizada y peering entre eu-west-1 y eu-central-1.
- `vpc-multi-az-layers` (T1) — Usar al diseñar la topología de una VPC: capas de subredes (pública, privada, datos), reparto en AZ, NAT, tablas de rutas y security groups.

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

## 15-artifacts-and-registry (T1) — 6/11

- `artifact-repository-port` (T1) — Usar al diseñar o cambiar cómo el pipeline publica, promueve, retiene y traza artefactos (imágenes OCI, JAR, npm) tras un puerto agnóstico del repositorio.
- `image-scanning` (T1) — Usar al configurar el escaneo de vulnerabilidades de imágenes y dependencias con Trivy o Grype: umbrales, exclusiones con caducidad y gate de CI.
- `promotion-between-environments` (T1) — Usar al definir cómo un artefacto avanza de dev a staging y prod: misma imagen por digest, sin rebuild, con gates y evidencias.
- `remote-repos-and-dependency-confusion-protection` (T1) — Usar al configurar proxies de Maven/npm/OCI y repos virtuales para evitar dependency confusion, typosquatting y descargas directas de internet.
- `retention-and-cleanup` (T1) — Usar al definir políticas de retención y limpieza de imágenes y paquetes (Harbor, Nexus, ECR) sin romper rollback ni trazabilidad.
- `sbom` (T1) — Usar al generar, almacenar y consumir SBOM (CycloneDX), cargarlos en Dependency-Track y gestionar VEX para priorizar vulnerabilidades.

## 16-ci-cd (T1) — 9/13

- `contract-gate` (T1) — Usar al integrar Pact en el pipeline: publicar contratos, verificar proveedor y bloquear el despliegue con can-i-deploy.
- `database-migration-step` (T1) — Usar al decidir cómo y cuándo se ejecutan las migraciones de base de datos dentro del pipeline de despliegue.
- `ephemeral-preview-environments` (T1) — Usar al crear entornos efímeros por PR (namespace en Kubernetes) para pruebas de integración, contrato y rendimiento, con limpieza y coste acotado.
- `github-actions` (T1) — Usar al escribir o revisar workflows de GitHub Actions: reutilizables, OIDC a la nube, pinning por SHA, runners efímeros, cachés, matrices y environments.
- `performance-gate` (T1) — Usar al añadir pruebas de rendimiento con JMeter al pipeline: umbrales, entorno comparable y detección de regresiones.
- `pipeline-architecture` (T1) — Usar al diseñar el pipeline CI/CD de un proyecto generado: etapas, orden de gates, separación CI/CD y artefactos inmutables.
- `quality-gates` (T1) — Usar al definir los gates de calidad bloqueantes del pipeline: tests, cobertura, mutación, arquitectura, estilo y análisis estático.
- `release-versioning-changelog` (T1) — Usar al definir versionado semántico, tags, changelog y notas de release automatizadas desde Conventional Commits.
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

## 22-polyglot-persistence (T1) — 11/21

- `audit-trail-without-event-sourcing` (T1) — Usar cuando se necesita historial de cambios o auditoría de negocio y se duda entre event sourcing y alternativas más simples (tabla de auditoría, Envers, CDC, temporal tables).
- `datastore-selection-guide` (T1) — Usar al elegir el almacén de datos de un agregado o caso de uso (Postgres, DynamoDB, OpenSearch, Redis) y al decidir si hace falta persistencia políglota.
- `dynamodb-data-modeling` (T1) — Usar al diseñar tablas, claves e índices de DynamoDB a partir de patrones de acceso (single-table vs multi-table, GSI, hot partitions).
- `dynamodb-event-store` (T1) — Usar al implementar un event store sobre DynamoDB: esquema de streams, append condicional, publicación desde DynamoDB Streams y límites.
- `gdpr-and-immutable-events` (T1) — Usar al diseñar eventos inmutables (event sourcing, logs, outbox) que contienen datos personales y hay que atender supresión o rectificación.
- `global-tables-and-write-region-rules` (T1) — Usar al replicar DynamoDB entre regiones (Global Tables): modo de consistencia, conflictos last-writer-wins y región de escritura por agregado o tenant.
- `mongodb-alternative` (T3) — Usar solo si se propone MongoDB (o compatible) en lugar de DynamoDB como almacén documental; referencia T3 con criterios y límites.
- `outbox-and-cdc` (T1) — Usar al publicar eventos tras un cambio en la base de datos sin doble escritura: patrón transactional outbox, relay por polling o CDC (Debezium, DynamoDB Streams).
- `polyglot-operations-cost` (T1) — Usar antes de añadir un almacén (DynamoDB, OpenSearch, Redis) a un proyecto, para estimar y aceptar su coste operativo y de equipo.
- `rebuilds-and-replays` (T1) — Usar al reconstruir proyecciones o read models de un sistema event-sourced desde el log de eventos (rebuild, replay, blue/green de proyecciones).
- `testing-event-sourced-systems` (T1) — Usar al escribir tests de aggregates, upcasters y proyecciones en sistemas event-sourced (given-when-then sobre eventos, replay, concurrencia).

## 23-data-platform (T2) — 0/15


## 24-ai-engineering (T2) — 0/21


## 25-security-operations (T2) — 0/16


## 26-enterprise-capabilities (T2) — 0/16


## 27-frontend-react (T1) — 0/23


## 28-local-kubernetes (T1) — 0/9


## 29-cloud-readiness (T1) — 0/6


## 30-engineering-process (T1) — 0/19


## 31-agentic-engineering (T1) — 5/13

- `bootstrap-generated-project-claude-config` (T1) — Usar en /project-init para crear el .claude/, CLAUDE.md y hooks de un proyecto generado a partir de las guías de la fábrica (sin plantillas).
- `claude-md-authoring` (T1) — Usar al escribir o editar un CLAUDE.md (de la fábrica o de un proyecto generado) para que sea corto y efectivo.
- `gate-protocol` (T1) — Usar al terminar una fase del flujo o antes de avanzar de gate; define cómo parar, pedir aprobación humana y registrarla.
- `skill-authoring-guide` (T1) — Usar al crear o revisar un skill de la fábrica; define anatomía obligatoria, niveles T1/T2/T3 y reglas de enforcement.
- `verify-before-asserting` (T1) — Usar antes de afirmar versiones, comportamiento de herramientas, normativa o que algo funciona; obliga a verificar o marcar TODO-VERIFY.
