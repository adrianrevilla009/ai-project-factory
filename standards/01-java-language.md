# Estándares · 01-java-language

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## code-style-and-naming

- **MUST** seguir las convenciones Java: `UpperCamelCase` clases/records, `lowerCamelCase` métodos y variables, `UPPER_SNAKE_CASE` constantes, paquetes en minúsculas sin guiones bajos.
- **MUST** que los identificadores y ficheros estén en inglés; los comentarios y documentación humana en español.
- **MUST** nombrar por intención del dominio (`overdueInvoices`), no por tipo (`list2`) ni abreviaturas crípticas (`cstmrLst`).
- **MUST** usar verbos para métodos y sustantivos para tipos; booleanos como pregunta (`isActive`, `hasPendingItems`).
- **MUST NOT** usar prefijos/sufijos vacíos (`IOrderService`, `OrderServiceImpl` cuando hay una sola implementación); nombrar la implementación por lo que la distingue (`JpaOrderRepository`).
- **SHOULD** métodos de ≤ ~30 líneas y una sola responsabilidad; clases cohesivas; complejidad ciclomática baja.
- **MUST NOT** dejar código comentado, `TODO` sin responsable/ticket, ni imports con comodín (`import x.*`).
- **SHOULD** comentar el *porqué*, no el *qué*; si hace falta explicar qué hace, renombrar o extraer.
- **MUST** delegar el formato (indentación, espacios, orden de imports) a una herramienta automática ejecutada en el build; **MUST NOT** discutir formato en revisión.
- **SHOULD** un tipo público de primer nivel por fichero; tests nombrados por comportamiento (`rejectsExpiredToken`).

## collections-and-streams

- **MUST** declarar variables, parámetros y retornos con la interfaz (`List`, `Map`), no la implementación.
- **MUST** devolver colecciones inmutables (`List.copyOf`, `Stream.toList()`, `Collections.unmodifiableList` solo como vista) desde APIs públicas.
- **MUST NOT** modificar una colección mientras se itera (`ConcurrentModificationException`); usar `removeIf` o construir una nueva.
- **MUST NOT** producir efectos laterales en `map`/`filter`/`peek`; `forEach` solo como operación terminal final.
- **MUST NOT** reutilizar un `Stream` ya consumido.
- **MUST NOT** usar `parallelStream()` en servicios web sin medir: comparte el `ForkJoinPool` común y bloquea otras peticiones.
- **SHOULD** usar un bucle `for` cuando el pipeline necesita más de ~4 pasos, estado mutable o manejo de excepciones checked.
- **SHOULD** dimensionar `HashMap`/`ArrayList` cuando el tamaño es conocido y grande.
- **MUST** usar `EnumMap`/`EnumSet` para claves enum, y `Collectors.toMap` con función de fusión si las claves pueden repetirse (si no, lanza `IllegalStateException`).
- **MUST NOT** usar `LinkedList` por defecto; `ArrayList` o `ArrayDeque`.

## equals-hashcode-tostring

- **MUST** sobrescribir `equals` y `hashCode` juntos, con los mismos campos.
- **MUST** respetar el contrato: reflexivo, simétrico, transitivo, consistente, `equals(null) == false`.
- **MUST NOT** incluir campos mutables en `hashCode` de objetos que se guardan en `HashSet`/claves de `HashMap`.
- **MUST** para entidades JPA: igualdad basada en identificador de negocio o en el id con manejo de `null` antes de persistir, y `hashCode` constante (p. ej. `getClass().hashCode()`); **MUST NOT** incluir asociaciones perezosas.
- **MUST NOT** incluir en `toString` secretos, contraseñas, tokens, datos personales ni asociaciones perezosas (provoca `LazyInitializationException` o N+1).
- **MUST** sobrescribir `toString` de un record que contenga datos sensibles para enmascararlos.
- **SHOULD** usar `Objects.equals`/`Objects.hash`; **MUST** comparar `double` con `Double.compare`.
- **SHOULD** que `compareTo` sea consistente con `equals`; si no, documentarlo.
- **MUST NOT** usar `==` para comparar `String` ni wrappers.

## exceptions-and-error-handling

- **MUST** lanzar excepciones específicas de dominio (`InsufficientStockException`) que extiendan `RuntimeException`; reservar checked exceptions para fallos recuperables que el llamante pueda tratar de forma distinta.
- **MUST** preservar la causa: `new DomainException("msg", e)`.
- **MUST NOT** capturar `Throwable` ni `Error`; **MUST NOT** capturar `Exception` salvo en un límite de proceso (consumidor de cola, handler global).
- **MUST NOT** tragar excepciones con `catch` vacío; si se ignora a propósito, comentar el motivo y registrar a nivel DEBUG.
- **MUST NOT** registrar y relanzar la misma excepción en cada capa (duplica el log): se registra una sola vez, en el límite que la gestiona.
- **MUST** usar try-with-resources para todo `AutoCloseable`.
- **MUST NOT** usar excepciones para control de flujo normal.
- **MUST NOT** incluir secretos o datos personales en el mensaje de la excepción.
- **SHOULD** validar argumentos con `IllegalArgumentException`/`IllegalStateException` y mensajes que incluyan el valor ofensor no sensible.
- **MUST** restaurar el flag de interrupción tras capturar `InterruptedException` (`Thread.currentThread().interrupt()`).

## generics-and-api-design

- **MUST** minimizar la superficie pública: paquete-privado por defecto, `public` solo para la API del módulo.
- **MUST NOT** usar tipos crudos (`List` sin parámetro) ni `@SuppressWarnings("unchecked")` sin comentario que justifique la seguridad.
- **MUST** aplicar PECS: `? extends T` para productores, `? super T` para consumidores; **MUST NOT** devolver tipos con comodines.
- **MUST** devolver tipos específicos y aceptar tipos generales (`Collection<? extends Item>` entrada, `List<Item>` salida).
- **SHOULD** limitar los parámetros a 3-4; con más, usar un record de parámetros o un builder explícito (sin Lombok).
- **MUST NOT** usar parámetros booleanos que cambien el comportamiento (`save(order, true)`); usar dos métodos o un enum.
- **MUST NOT** devolver arrays ni `null` como "sin resultado" (ver `null-safety`).
- **SHOULD** preferir composición a herencia; marcar `final` o `sealed` lo que no se diseñó para extender.
- **SHOULD** que las interfaces sean pequeñas y con un propósito (segregación); no crear interfaz para cada clase sin segundo implementador.
- **MUST** documentar con Javadoc el contrato (precondiciones, excepciones, hilo-seguridad) de la API pública.
- **MUST** tratar los cambios incompatibles de API como cambio mayor (ver `backward-compatibility-rules`).

## immutability-and-value-objects

- **MUST** modelar value objects (`Email`, `OrderId`, `Money`) como `record` o clase `final` con campos `final`.
- **MUST** validar invariantes en el constructor canónico del record; no debe existir una instancia inválida.
- **MUST** hacer copia defensiva de colecciones recibidas: `List.copyOf(items)` en el constructor.
- **MUST NOT** exponer colecciones mutables; devolver vistas inmutables o copias.
- **MUST NOT** usar `String` o `long` desnudos para identificadores de dominio distintos (primitive obsession): un `CustomerId` no es un `OrderId`.
- **SHOULD** usar métodos `withX(...)` que devuelven una copia nueva en lugar de setters.
- **SHOULD** marcar las clases como `final` salvo diseño explícito para herencia.
- **MUST NOT** usar `Date` ni arrays mutables como campos de un value object sin copiarlos.

## jvm-in-containers

- **MUST** fijar `resources.requests` y `resources.limits` de memoria iguales (QoS Guaranteed/predecible) y declarar CPU request.
- **MUST** dimensionar el heap como porcentaje del límite del contenedor con `-XX:MaxRAMPercentage` (típico 60-75 %); **MUST NOT** fijar `-Xmx` en valor absoluto que ignore el límite del pod.
- **MUST** dejar margen para memoria fuera del heap (metaspace, hilos, buffers directos, código compilado): heap + no-heap debe caber en el límite.
- **MUST** arrancar con `-XX:+ExitOnOutOfMemoryError` para que Kubernetes reinicie el pod en vez de quedar medio vivo.
- **SHOULD** activar `-XX:+HeapDumpOnOutOfMemoryError` con `-XX:HeapDumpPath` en un volumen con espacio, solo si el dump no filtra datos personales fuera de los controles.
- **MUST** ejecutar como usuario no root, imagen base mínima y sin shell innecesaria (ver estándares de contenedores, ADR-0018).
- **SHOULD** pasar opciones con `JAVA_TOOL_OPTIONS` o `JAVA_OPTS` documentadas, no en el `ENTRYPOINT` en duro.
- **SHOULD** dejar que la JVM detecte los CPU del cgroup; **MUST NOT** fijar `-XX:ActiveProcessorCount` sin medir.
- **MUST** configurar `terminationGracePeriodSeconds` mayor que el apagado ordenado de la aplicación (ver `graceful-shutdown-lifecycle`).
- **SHOULD** medir con carga antes de elegir GC; el GC por defecto suele bastar. TODO-VERIFY valores por versión de JDK.

## logging-rules

- **MUST** usar la fachada SLF4J con un logger `private static final` por clase; **MUST NOT** usar `System.out/err` ni `printStackTrace()`.
- **MUST** usar placeholders (`log.info("order {} paid", id)`), nunca concatenación.
- **MUST** pasar la excepción como último argumento (`log.error("charge failed for order {}", id, e)`) para conservar la traza.
- **MUST NOT** registrar secretos, tokens, contraseñas, números de tarjeta, ni datos personales sin enmascarar.
- **MUST NOT** registrar cuerpos completos de petición/respuesta por defecto.
- **MUST** respetar los niveles: ERROR = requiere acción; WARN = anómalo pero recuperado; INFO = hitos de negocio; DEBUG/TRACE = diagnóstico, apagado por defecto.
- **MUST NOT** registrar y relanzar la misma excepción (ver `exceptions-and-error-handling`).
- **SHOULD** emitir logs estructurados (JSON) con `traceId` y `spanId` vía MDC; limpiar el MDC al terminar la tarea.
- **SHOULD** proteger logs costosos de construir con `log.isDebugEnabled()` o suplier lambda.
- **MUST NOT** registrar dentro de bucles calientes sin muestreo.

## modern-java-idioms

- **MUST** usar `record` para portadores de datos inmutables (DTO, eventos, value objects simples) en lugar de clases con getters manuales o Lombok (D27).
- **MUST** usar `switch` como expresión con `->`, sin `break` ni fall-through accidental.
- **SHOULD** modelar variantes cerradas con `sealed interface` + records y `switch` con pattern matching sin `default`, para que el compilador exija exhaustividad.
- **SHOULD** usar `instanceof` con patrón (`if (o instanceof Foo f)`) en vez de cast manual.
- **SHOULD** usar text blocks (`"""`) para JSON/SQL/GraphQL embebido en tests o consultas fijas.
- **SHOULD** usar `var` solo cuando el tipo es evidente en la misma línea (`var users = new ArrayList<User>()`).
- **MUST NOT** usar `var` para tipos devueltos por métodos cuyo nombre no revela el tipo, ni en lambdas con parámetros ambiguos.
- **MUST NOT** añadir un `default` a un `switch` sobre un `sealed` solo para silenciar al compilador: oculta variantes nuevas.
- **SHOULD** preferir `Stream.toList()` (inmutable) a `collect(Collectors.toList())`.

## no-lombok

- **MUST NOT** añadir la dependencia `org.projectlombok:lombok` ni su procesador de anotaciones (ADR-0027).
- **MUST NOT** importar nada de `lombok.*` (`@Data`, `@Getter`, `@Builder`, `@Slf4j`, `@RequiredArgsConstructor`, `val`...).
- **MUST** usar `record` para datos inmutables (getters, `equals`, `hashCode`, `toString` generados por el lenguaje).
- **MUST** escribir builders explícitos cuando haya muchos parámetros opcionales (ver `generics-and-api-design`) o usar un record de opciones.
- **MUST** declarar el logger a mano: `private static final Logger log = LoggerFactory.getLogger(Foo.class);`.
- **MUST** escribir constructores explícitos para inyección de dependencias (un solo constructor, Spring lo inyecta sin anotación).
- **SHOULD** que el IDE genere getters/constructores cuando una clase mutable (entidad JPA) los necesite.
- **MUST NOT** introducir sustitutos que hagan lo mismo con generación de código opaca (p. ej. Immutables, AutoValue) sin ADR nuevo.

## null-safety

- **MUST** tratar `null` como "no permitido" salvo que el contrato diga lo contrario; validar en el borde con `Objects.requireNonNull(x, "x")`.
- **MUST** devolver `Optional<T>` desde métodos de búsqueda que puedan no encontrar resultado.
- **MUST NOT** devolver `null` desde métodos que devuelven colecciones o arrays: devolver colección vacía.
- **MUST NOT** usar `Optional` como campo, parámetro de método ni elemento de colección.
- **MUST NOT** llamar `Optional.get()` sin comprobación; usar `orElseThrow(() -> new NotFoundException(...))`, `map`, `ifPresent` u `orElse`.
- **SHOULD** declarar la política de nulos del paquete con anotaciones (`@NullMarked` de JSpecify o equivalente de Spring) — TODO-VERIFY soporte en la versión de Spring Boot elegida.
- **SHOULD** usar `Objects.requireNonNullElse` / `Map.getOrDefault` antes que comprobaciones manuales repetidas.
- **MUST NOT** devolver `Boolean` nulo como tercer estado; usar un enum.

## profiling-and-leaks

- **MUST** medir antes de optimizar: definir la métrica (p99, throughput, heap tras GC), reproducir, cambiar una cosa, volver a medir.
- **MUST** perfilar con la herramienta del JDK primero: Java Flight Recorder (`jcmd <pid> JFR.start`) y `jcmd <pid> Thread.print`, `GC.heap_info`.
- **MUST** distinguir fuga de uso alto: una fuga es heap *después de GC completos* creciente en el tiempo.
- **MUST** capturar un heap dump (`jcmd <pid> GC.heap_dump`) en dos instantes y comparar los objetos retenidos (analizador como Eclipse MAT); buscar el camino al GC root.
- **MUST** tratar los heap dumps como datos sensibles: pueden contener credenciales y datos personales; no subirlos a herramientas externas ni a tickets.
- **MUST NOT** perfilar en producción con agentes de alto coste sin aprobación; JFR con configuración por defecto es de bajo overhead (TODO-VERIFY cifras).
- **SHOULD** vigilar causas típicas: cachés sin límite ni expiración, `ThreadLocal` no limpiado en pools, listeners no desregistrados, colecciones estáticas, `ClassLoader` retenido, conexiones/streams sin cerrar.
- **SHOULD** usar JMH para microbenchmarks; **MUST NOT** medir con `System.currentTimeMillis` en bucle y sin calentamiento.
- **SHOULD** exponer métricas JVM (heap, GC, hilos) y alertar sobre tendencias.

## strings-encoding-locale

- **MUST** indicar el charset explícito en toda conversión: `s.getBytes(StandardCharsets.UTF_8)`, `new String(bytes, StandardCharsets.UTF_8)`, `Files.readString(path, UTF_8)`.
- **MUST** usar UTF-8 en ficheros, HTTP, BD y mensajería; no depender de `file.encoding` del sistema.
- **MUST** pasar `Locale` explícito a `toLowerCase`/`toUpperCase`/`String.format` cuando el resultado es un identificador técnico: usar `Locale.ROOT` (evita el problema del turco: `"TITLE".toLowerCase()` produce "tıtle" con `tr`).
- **MUST** usar `Locale` del usuario solo para presentación; formatos intercambiables (JSON, CSV, logs) usan `Locale.ROOT`/ISO-8601.
- **MUST NOT** comparar texto del usuario con `==` ni con `equals` cuando importa el caso o los acentos; usar `equalsIgnoreCase` para ASCII o `java.text.Normalizer` (NFC) + `Collator` para texto humano.
- **MUST NOT** concatenar con `+` dentro de bucles; usar `StringBuilder` o `String.join`.
- **MUST NOT** construir SQL, HTML, rutas o comandos concatenando entrada del usuario (ver `sql-injection-prevention`).
- **SHOULD** usar `isBlank()`, `strip()` (Unicode) en lugar de `trim()` y `split` con regex cuando basta con otra API.
- **MUST** precompilar los `Pattern` reutilizados (`static final`) y evitar regex con retroceso catastrófico sobre entrada externa (ReDoS).

## time-and-money

- **MUST** usar `java.time` (`Instant`, `LocalDate`, `ZonedDateTime`, `Duration`); **MUST NOT** usar `Date`, `Calendar` ni `SimpleDateFormat` (no seguro entre hilos).
- **MUST** almacenar y transmitir instantes en UTC (`Instant`, ISO-8601); convertir a zona local solo en presentación.
- **MUST** indicar `ZoneId` explícito; **MUST NOT** depender de la zona por defecto del servidor.
- **MUST** inyectar `java.time.Clock` en lugar de llamar a `Instant.now()` en lógica de negocio, para poder fijar el tiempo en tests.
- **MUST NOT** usar `double`/`float` para dinero; usar `BigDecimal` con escala y `RoundingMode` explícitos, o enteros en unidad mínima (céntimos).
- **MUST** crear `BigDecimal` con `BigDecimal.valueOf(...)` o desde `String`, nunca `new BigDecimal(double)`.
- **MUST** modelar el dinero como `Money(BigDecimal amount, Currency currency)` y rechazar operaciones entre divisas distintas.
- **MUST** comparar `BigDecimal` con `compareTo`, no `equals` (distingue escala).
- **SHOULD** usar `Duration` para intervalos y `Period` para calendario; **MUST NOT** sumar 24 h para "un día" en zonas con cambio horario.
