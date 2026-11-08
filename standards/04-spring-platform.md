# Estándares · 04-spring-platform

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## actuator-and-health

- **MUST** incluir `spring-boot-starter-actuator` y exponer solo lo necesario: `management.endpoints.web.exposure.include=health,info,prometheus` (lista explícita).
- **MUST NOT** usar `include=*` ni exponer `env`, `heapdump`, `threaddump`, `beans`, `configprops` sin autenticación.
- **MUST** habilitar sondas: `management.endpoint.health.probes.enabled=true` y usar los grupos `liveness` y `readiness`.
- **MUST** mantener el liveness sin dependencias externas (BD, brokers): solo indica si el proceso está atascado. Las dependencias críticas van en readiness.
- **SHOULD** servir la gestión en un puerto separado (`management.server.port`) no publicado por el ingress.
- **SHOULD** `management.endpoint.health.show-details=when-authorized` (o `never` hacia fuera).
- **SHOULD** crear `HealthIndicator` propios con timeout corto; un indicador lento tumba la sonda.
- **MUST NOT** convertir un fallo de una dependencia opcional en readiness DOWN si el servicio puede degradarse (ver `resilience`).

## configuration-properties

- **MUST** agrupar la configuración propia bajo un prefijo y mapearla con `@ConfigurationProperties` sobre un `record` inmutable.
- **MUST** anotar con `@Validated` y restricciones Jakarta (`@NotBlank`, `@Min`, `@NotNull`) para que el arranque falle ante configuración inválida.
- **MUST** registrar las clases con `@ConfigurationPropertiesScan` o `@EnableConfigurationProperties`.
- **MUST NOT** esparcir `@Value("${...}")` por la lógica de negocio; reservarlo para casos puntuales y triviales.
- **MUST NOT** guardar secretos en `application*.yml` ni en el repositorio; se inyectan por entorno o gestor de secretos. Los ejemplos usan valores `changeme`.
- **SHOULD** usar `Duration` y `DataSize` en vez de números sin unidad.
- **SHOULD** dar valores por defecto seguros con `@DefaultValue` y diferenciar entornos con perfiles o variables, no con ramas `if` en código.
- **SHOULD** añadir `spring-boot-configuration-processor` para metadatos de IDE (comprobar configuración Maven).

## controllers-and-validation

- **MUST** mantener el controlador fino: traduce HTTP a una llamada de servicio de aplicación; sin lógica de negocio ni acceso a repositorios.
- **MUST** usar DTOs (`record`) de entrada y salida; **MUST NOT** exponer entidades JPA en la API.
- **MUST** validar la entrada con `@Valid`/`@Validated` y restricciones Jakarta (`@NotBlank`, `@Size`, `@Positive`, `@Email`).
- **MUST** validar `@PathVariable` y `@RequestParam` anotando la clase con `@Validated`.
- **MUST** devolver códigos HTTP correctos (201 + `Location` al crear, 204 sin cuerpo, 404, 409) y delegar errores en el manejador global (`error-handling-problem-details`).
- **MUST NOT** aceptar `Map<String, Object>` ni campos desconocidos sin control como cuerpo; evitar mass assignment con DTOs específicos por caso de uso.
- **SHOULD** limitar tamaños (`@Size(max=...)`, `spring.servlet.multipart.max-file-size`) para prevenir abuso.
- **SHOULD** una validación de negocio (unicidad, estado) hacerla en el servicio, no con anotaciones.

## dependency-injection-rules

- **MUST** inyectar por constructor con campos `final`; con un único constructor no hace falta `@Autowired`.
- **MUST NOT** usar `@Autowired` sobre campos ni setters en código de producción.
- **MUST NOT** usar `ApplicationContext.getBean(...)` como service locator.
- **MUST NOT** introducir dependencias circulares; refactorizar (extraer un tercer bean o publicar un evento). No activar `spring.main.allow-circular-references`.
- **SHOULD** limitar un bean a ~5 dependencias; más indica responsabilidades mezcladas.
- **SHOULD** inyectar interfaces o tipos mínimos necesarios, no implementaciones concretas ni `EntityManager` en controladores.
- **MUST** usar `@Qualifier` o un tipo propio cuando existan varios beans del mismo tipo; no depender del nombre del parámetro.
- **MUST NOT** usar Lombok (`@RequiredArgsConstructor`) (D27); escribir el constructor.

## domain-events-in-spring

- **MUST** nombrar eventos en pasado y como hechos de negocio (`OrderPlaced`), inmutables (`record`).
- **MUST** que el evento lleve identificadores y datos mínimos, no entidades JPA (evita `LazyInitializationException` y acoplamiento).
- **MUST** consumir con `@TransactionalEventListener(phase = AFTER_COMMIT)` cuando el efecto no deba ocurrir si la transacción hace rollback.
- **MUST** que los listeners con efectos externos sean idempotentes: pueden ejecutarse más de una vez.
- **SHOULD** usar `@ApplicationModuleListener` de Spring Modulith (asíncrono, transaccional propio) y su registro de publicación de eventos para no perder eventos tras un fallo.
- **MUST NOT** publicar a un broker desde el listener y escribir además en otra base de datos sin outbox (sin doble escritura; ver `transactional-outbox`).
- **MUST NOT** depender del orden entre listeners.
- **SHOULD** que el evento cruce el límite del módulo solo si está en su API pública (`project-layout`).

## error-handling-problem-details

- **MUST** responder errores con `application/problem+json` usando `ProblemDetail` de Spring (RFC 9457, que sustituye a RFC 7807).
- **MUST** centralizar el mapeo en un único `@RestControllerAdvice`, preferiblemente extendiendo `ResponseEntityExceptionHandler`.
- **MUST** incluir `type` (URI estable por tipo de error), `title`, `status`, `detail` e `instance`; añadir extensiones propias (`code`, `errors`) mediante propiedades.
- **MUST NOT** devolver trazas, nombres de clase, SQL ni mensajes de excepción internos en `detail`; los 500 llevan un mensaje genérico y un identificador de correlación.
- **MUST** registrar el error completo en el log con el mismo identificador de correlación (nivel ERROR solo para 5xx).
- **MUST** mapear errores de validación a 400 con la lista de campos inválidos; conflictos de negocio a 409; no encontrado a 404.
- **SHOULD** definir excepciones de dominio sin dependencia de Spring y traducirlas en el advice.
- **SHOULD** valorar `spring.mvc.problemdetails.enabled=true` para errores estándar de Spring MVC (verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08).

## file-upload-and-streaming

- **MUST** configurar límites explícitos: `spring.servlet.multipart.max-file-size`, `max-request-size` y límite a nivel de proxy/gateway.
- **MUST NOT** usar `file.getBytes()` ni cargar el fichero entero en memoria; usar `getInputStream()` y copiar por flujo.
- **MUST NOT** usar `getOriginalFilename()` como ruta de destino; generar un nombre propio (UUID) y guardar el original como metadato.
- **MUST** cerrar los streams (try-with-resources) y manejar el fallo parcial (borrar el parcial).
- **SHOULD** subir ficheros grandes directamente al almacenamiento de objetos con URL prefirmada en lugar de pasar por el servicio.
- **MUST** servir descargas con `StreamingResponseBody` o `InputStreamResource`, con `Content-Disposition` y `Content-Type` explícitos.
- **MUST** que las exportaciones grandes lean por páginas/cursor, no `findAll()`.
- **MUST** comprobar autorización sobre el recurso antes de abrir el stream.
- **SHOULD** declarar el almacén detrás de una interfaz (`FileStorage`) para cambiar disco local por S3 sin tocar el controlador. En local no se reproduce S3 real; se usa un emulador (preparado para AWS, no verificado en real).

## graceful-shutdown-lifecycle

- **MUST** activar `server.shutdown=graceful` y fijar `spring.lifecycle.timeout-per-shutdown-phase` (p. ej. `25s`).
- **MUST** que el timeout de la fase sea menor que el periodo de gracia del orquestador (en Kubernetes, `terminationGracePeriodSeconds`) con margen.
- **MUST** dejar de recibir tráfico antes de parar: readiness pasa a DOWN al iniciar el apagado (comportamiento de Spring Boot con probes) y se considera un pequeño `preStop` de espera para la propagación del balanceador.
- **MUST** liberar recursos en `@PreDestroy` o `SmartLifecycle`/`DisposableBean`, de forma rápida e idempotente.
- **MUST** que los executors propios usen `setWaitForTasksToCompleteOnShutdown(true)` y `setAwaitTerminationSeconds(...)`; no crear `new Thread` sin gestión.
- **MUST** que los consumidores de mensajes dejen de consumir y terminen o devuelvan los mensajes en curso antes de cerrar (ver `delivery-semantics`).
- **SHOULD** diseñar las operaciones para ser idempotentes: un SIGKILL tras el timeout puede cortar trabajo.
- **MUST NOT** capturar SIGTERM manualmente ni usar `System.exit` en código de negocio.

## http-clients-and-timeouts

- **MUST** definir timeout de conexión y de lectura explícitos en todo cliente; el valor por defecto del JDK/librería puede ser infinito o muy alto.
- **MUST** construir los clientes desde el builder inyectado (`RestClient.Builder`, `WebClient.Builder`) para heredar observabilidad y codecs de Spring Boot.
- **MUST NOT** hacer `new RestTemplate()` ni `HttpClient.newHttpClient()` sueltos en código de negocio.
- **MUST** externalizar URL base y timeouts en `@ConfigurationProperties` (ver `configuration-properties`), un bloque por dependencia.
- **MUST** que el timeout total de la petición entrante sea mayor que la suma de timeouts salientes encadenados (presupuesto de latencia).
- **SHOULD** preferir `RestClient` (Spring Framework 6.1+) en código bloqueante y `WebClient` solo en stacks reactivos.
- **SHOULD** reintentar solo operaciones idempotentes y combinarlo con `resilience`.
- **MUST NOT** registrar cuerpos, cabeceras `Authorization` ni tokens en logs de cliente.

## mapping-mapstruct

- **MUST** usar MapStruct (generación en compilación) en lugar de mapeadores por reflexión (ModelMapper, Dozer).
- **MUST** declarar `@Mapper(componentModel = "spring")` para inyectar el mapper por constructor.
- **MUST** configurar `unmappedTargetPolicy = ReportingPolicy.ERROR` para que un campo nuevo sin mapear rompa la compilación.
- **MUST NOT** poner lógica de negocio, acceso a repositorios ni llamadas remotas en un mapper.
- **MUST** mapear a/desde `record` o clases con constructor; sin Lombok (D27). Si se usan ambos, requeriría `lombok-mapstruct-binding`; está fuera de política.
- **SHOULD** un mapper por módulo y por dirección clara (`toResponse`, `toEntity`); no mapeos bidireccionales genéricos.
- **SHOULD** mapear colecciones con el método generado y, para entidades JPA, evitar disparar cargas perezosas (mapear desde proyecciones o relaciones ya cargadas).
- **MUST** testear mappers con casos de campos sensibles (ocultar `passwordHash`, fechas, enums).

## project-layout

- **MUST** organizar el código por módulo de negocio (`order`, `billing`, `customer`), no por capa técnica global (`controller/`, `service/`, `repository/`).
- **MUST** colocar cada módulo como subpaquete directo del paquete raíz de la aplicación; la clase `@SpringBootApplication` vive en el paquete raíz.
- **MUST** exponer solo la API del módulo en su paquete raíz (servicio de aplicación, DTOs, eventos); lo demás va en subpaquetes internos (`internal`).
- **MUST NOT** acceder a clases internas de otro módulo ni crear dependencias cíclicas entre módulos.
- **MUST** incluir un test que ejecute `ApplicationModules.of(Application.class).verify()`.
- **SHOULD** comunicar módulos mediante eventos (ver `domain-events-in-spring`) cuando no se necesite respuesta síncrona.
- **SHOULD** dentro de cada módulo separar `web`, `application`, `domain`, `infrastructure` solo si el módulo lo justifica; no crear capas vacías.
- **MUST NOT** usar Lombok (D27); usar `record` y constructores explícitos.

## reactive-vs-blocking

- **MUST** por defecto usar Spring MVC bloqueante (Java + Spring Boot + Maven); justificar WebFlux con un ADR del proyecto.
- **SHOULD** activar hilos virtuales (`spring.threads.virtual.enabled=true`, Boot 3.2+, requiere Java 21+; verificado en el apéndice de propiedades de Spring Boot 4.x el 2026-11-08) antes de plantear reactivo por escalabilidad de I/O.
- **MUST** elegir WebFlux solo con necesidad real: streaming/backpressure (SSE, WebSocket), fan-out masivo, o stack reactivo completo.
- **MUST NOT** mezclar JDBC/JPA bloqueante dentro de un pipeline reactivo; si hay JPA, el servicio es bloqueante.
- **MUST NOT** llamar a `.block()` en hilos del event loop.
- **MUST** envolver código bloqueante inevitable con `Schedulers.boundedElastic()`.
- **SHOULD** usar `WebClient` desde MVC solo para composición asíncrona puntual; para llamadas simples usar `RestClient`.
- **MUST** que el equipo conozca depuración y testing reactivos (`StepVerifier`) antes de adoptarlo.

## resilience

- **MUST** poner un timeout de cliente (`http-clients-and-timeouts`) antes de añadir cualquier patrón; resiliencia sin timeout no protege.
- **MUST** reintentar solo operaciones idempotentes o con clave de idempotencia, con backoff exponencial y jitter, y número máximo bajo (2-3).
- **MUST** definir `fallback` explícito y de significado de negocio claro, o dejar propagar el error; **MUST NOT** devolver listas vacías o `null` que oculten el fallo.
- **MUST** configurar instancias por nombre en `application.yml`, una por dependencia, no valores en anotaciones.
- **MUST** usar `Bulkhead` (semáforo) para limitar concurrencia hacia dependencias lentas.
- **SHOULD** orden de composición documentado: Retry envuelve a CircuitBreaker, que envuelve a TimeLimiter/Bulkhead (comprobar el orden real de aspectos, comprobar al fijar la versión).
- **SHOULD** exponer métricas y estado de los breakers vía Actuator (`actuator-and-health`).
- **MUST NOT** hacer retry anidado en varias capas (multiplica la carga: 3x3x3).

## spring-data-rules

- **MUST** definir `@Transactional` en la capa de servicio de aplicación, nunca en controladores ni repositorios.
- **MUST** marcar las lecturas con `@Transactional(readOnly = true)`.
- **MUST** fijar `spring.jpa.open-in-view=false`.
- **MUST** usar `Pageable` con tamaño máximo acotado en listados; **MUST NOT** devolver `findAll()` sin límite en endpoints.
- **MUST NOT** devolver entidades fuera del servicio; devolver DTOs o proyecciones (ver `mapping-mapstruct`).
- **MUST** cargar relaciones de forma explícita (ver `n-plus-one`).
- **SHOULD** usar `@Query` explícita cuando el nombre derivado supere ~3 condiciones; los nombres largos son frágiles.
- **MUST NOT** llamar a métodos `@Transactional` de la misma clase (auto-invocación): el proxy no se aplica.
- **MUST NOT** hacer llamadas HTTP lentas dentro de una transacción abierta.
- **SHOULD** usar `@Modifying` con consultas de actualización masiva y `clearAutomatically` solo si se entiende el efecto en el contexto de persistencia.

## startup-and-native

- **MUST** medir antes de optimizar: registrar tiempo de arranque (log `Started ... in X seconds`) y memoria base como línea base.
- **MUST** arrancar con JVM estándar por defecto; la imagen nativa es opt-in con justificación en un ADR del proyecto.
- **SHOULD** probar primero opciones baratas: eliminar auto-configuraciones y dependencias no usadas, CDS/AppCDS, `spring.main.lazy-initialization` (con cautela: oculta errores de cableado hasta la primera petición).
- **MUST** que, si se adopta nativo, el build nativo se ejecute en CI y los tests corran también en modo nativo (`native:test`, comprobar al fijar la versión).
- **MUST** declarar hints para reflexión/recursos (`RuntimeHintsRegistrar`, `@RegisterReflectionForBinding`) en lugar de ficheros JSON manuales cuando sea posible.
- **MUST NOT** usar reflexión dinámica, proxies o carga de clases en tiempo de ejecución sin comprobar su compatibilidad AOT.
- **MUST NOT** asumir que una librería es compatible con nativo; verificar su soporte en su documentación.
- **SHOULD** limitar el trabajo en `@PostConstruct` y `ApplicationRunner` (conexiones remotas, cargas masivas): bloquean el arranque y la readiness.

## testing-slices

- **MUST** preferir test unitario sin contexto; luego slice; `@SpringBootTest` solo para integración de extremo a extremo del servicio.
- **MUST** usar `@WebMvcTest(Controller.class)` para controladores (validación, serialización, códigos HTTP, Problem Details).
- **MUST** usar `@DataJpaTest` con una base real vía Testcontainers (misma BD que producción) para repositorios; **MUST NOT** probar queries nativas contra H2.
- **MUST** usar `@JsonTest` para contratos de serialización críticos.
- **MUST** sustituir colaboradores con `@MockitoBean` (Spring Framework 6.2+; en versiones anteriores `@MockBean`, comprobar al fijar la versión) y limitar su uso: muchos mocks indican un slice mal elegido.
- **SHOULD** reutilizar contenedores entre tests (singleton / `@ServiceConnection`, Boot 3.1+) para no multiplicar el tiempo.
- **MUST NOT** usar `@DirtiesContext` salvo causa documentada: destruye la caché de contextos.
- **MUST** que los tests no dependan del orden ni de datos de otros tests.

## upgrade-policy

- **MUST** estar en una línea de Spring Boot con soporte OSS vigente; comprobar las fechas de fin de soporte en la página oficial de versiones (comprobar al fijar la versión, no fijadas aquí).
- **MUST** subir versiones de parche dentro de la línea con frecuencia (mensual como objetivo) y por PR automático.
- **MUST** subir de línea menor/mayor de una en una, sin saltos, siguiendo la guía de migración oficial (Release Notes y Migration Guide del wiki de Spring Boot).
- **MUST** eliminar APIs `@Deprecated` en la línea actual antes de saltar a la siguiente.
- **MUST** gestionar versiones por el BOM de Spring Boot (`bom-management`); **MUST NOT** fijar a mano versiones de librerías que el BOM ya gestiona sin comentario justificado.
- **MUST** una subida por PR, con suite completa verde y sin mezclar cambios funcionales.
- **SHOULD** compatibilidad de Spring Cloud/Modulith verificada en su matriz oficial antes de subir Boot.
- **SHOULD** ejecutar OpenRewrite o la herramienta de migración oficial como ayuda, revisando el diff (comprobar receta disponible).
- **MUST NOT** usar versiones SNAPSHOT/milestone/RC en ramas de producción.
