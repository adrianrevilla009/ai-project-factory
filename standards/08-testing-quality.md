# Estándares · 08-testing-quality

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## api-testing

- **MUST** probar por endpoint: camino feliz, validación inválida (400/422), no encontrado (404), conflicto (409) y no autorizado/prohibido (401/403).
- **MUST** verificar el formato de error `application/problem+json` (ver `error-handling-problem-details`) y que no filtra trazas ni detalles internos.
- **MUST** probar autorización con usuarios/roles distintos, incluido acceso a recursos de otro tenant o usuario (BOLA/IDOR).
- **MUST** aserciones sobre el JSON con rutas concretas (`jsonPath`), no comparar cuerpos como cadenas enteras.
- **SHOULD** usar `@WebMvcTest` + MockMvc para capa web aislada y `@SpringBootTest(webEnvironment = RANDOM_PORT)` con RestAssured o `RestClient` para flujos completos.
- **SHOULD** validar las respuestas contra el esquema OpenAPI del contrato (ver `openapi-contract-first`).
- **SHOULD** cubrir paginación, orden y límites máximos de página.
- **MUST NOT** usar puertos fijos ni compartir estado entre tests.
- **MUST NOT** deshabilitar la seguridad en los tests de API para "simplificar".

## architecture-testing-archunit

- **MUST** codificar como test ArchUnit cada regla arquitectónica que pueda romperse con un `import`.
- **MUST** ejecutarlos con Surefire en cada build (son tests unitarios rápidos).
- **MUST** importar solo las clases de producción (`ImportOption.DoNotIncludeTests`).
- **MUST** que cada regla tenga mensaje con `.because("...")` que explique el porqué y enlace al ADR/skill.
- **SHOULD** reutilizar las reglas de `policies/archunit/` copiándolas al módulo de test del proyecto.
- **SHOULD** añadir reglas de ciclos (`slices().matching(...).should().beFreeOfCycles()`).
- **SHOULD** tratar la deuda existente con `FreezingArchRule` y un plan de reducción, no con exclusiones silenciosas.
- **MUST NOT** relajar o borrar una regla para que pase el build sin ADR que lo justifique.
- **MUST NOT** usar `@SuppressWarnings`-style excepciones amplias (`resideInAnyPackage("..")`) que vacían la regla.

## bdd

- **MUST** redactar escenarios en lenguaje de dominio (Given/When/Then), sin detalles de UI, SQL ni HTTP.
- **MUST** un escenario = un comportamiento, con datos mínimos y explícitos en el propio escenario.
- **MUST** que los escenarios sean independientes y deterministas (sin orden entre ellos).
- **SHOULD** ejecutarlos contra la capa de aplicación o API, no a través de navegador, salvo recorridos críticos (ver `e2e-testing`).
- **SHOULD** usar `Scenario Outline` solo para variaciones de datos de la misma regla.
- **SHOULD** que los step definitions sean finos y deleguen en un helper de dominio; sin lógica de negocio en ellos.
- **MUST NOT** reutilizar steps con estado compartido global entre escenarios.
- **MUST NOT** convertir cada test unitario en un `.feature`.

## canary-analysis-and-synthetic-monitoring

- **MUST** definir antes del release las métricas de decisión (tasa de errores, latencia p95/p99, saturación, métrica de negocio) y los umbrales de promoción y de rollback, derivados del SLO.
- **MUST** comparar el canary contra la línea base estable (misma ventana, mismo tráfico) y no contra valores absolutos aislados.
- **MUST** exigir un volumen mínimo de tráfico y duración mínima antes de decidir; con poco tráfico, apoyarse en sintéticos.
- **MUST** que el rollback sea automático o de un paso, y probado.
- **MUST** tener sondas sintéticas de los flujos críticos (login, lectura clave, escritura de bajo riesgo) que usen datos de prueba etiquetados y sin efectos de negocio reales.
- **MUST NOT** usar credenciales o datos reales de clientes en sintéticos; credenciales desde el gestor de secretos.
- **MUST NOT** alertar por causa (CPU) lo que se puede alertar por síntoma (ver `alerting-symptom-based`).
- **SHOULD** diferenciar tráfico sintético en métricas y trazas con una cabecera o atributo dedicado.
- **SHOULD** incluir en el análisis el error budget restante: sin presupuesto, no se promueve (ver `slo-sli-error-budgets`).

## chaos-engineering

- **MUST** formular una hipótesis de estado estable medible ("p95 < 300 ms y errores < 1 % con un pod menos") antes de inyectar el fallo.
- **MUST** limitar el radio de explosión (un servicio, un namespace, un porcentaje) y definir condición de aborto y rollback.
- **MUST** tener observabilidad activa durante el experimento (métricas, trazas, alertas).
- **MUST** empezar en local/entorno de pruebas y con un solo fallo a la vez.
- **MUST NOT** ejecutar experimentos sin aviso al equipo ni fuera de la ventana acordada.
- **MUST NOT** activar Chaos Monkey por defecto: debe estar desactivado salvo perfil explícito.
- **SHOULD** usar la herramienta adecuada: **Chaos Monkey for Spring Boot** (fallos de aplicación: latencia, excepciones, kill de la app), **Toxiproxy** (red entre procesos: latencia, corte, ancho de banda; ideal en tests de integración), **Chaos Mesh** (fallos de pod, red, I/O en Kubernetes).
- **SHOULD** registrar cada game day: hipótesis, resultado, hallazgos y acciones con dueño.
- **SHOULD** automatizar los experimentos que resultaron valiosos como tests de resiliencia (ver `resilience-testing`).

## code-review-guidelines

- **MUST** revisar en este orden: (1) corrección y requisitos, (2) tests, (3) seguridad, (4) diseño y límites de capas, (5) legibilidad, (6) estilo (lo automatizable lo decide la herramienta, no el revisor).
- **MUST** que el PR sea revisable: un solo propósito, descripción con el porqué y enlace al requisito. Objetivo orientativo: menos de 400 líneas cambiadas; si es mayor, dividirlo.
- **MUST** que CI esté en verde antes de pedir revisión humana.
- **MUST** que cada comentario bloqueante indique el riesgo concreto; el resto se marca `nit:` o `suggestion:`.
- **MUST** verificar que hay test que falla sin el cambio (o justificación explícita).
- **MUST NOT** aprobar sin haber leído el diff completo ni aprobar tu propio PR.
- **MUST NOT** aceptar `@SuppressWarnings`, `@Disabled` o exclusiones de análisis sin motivo escrito.
- **SHOULD** responder a una revisión en menos de un día laborable; **SHOULD** preferir pair/revisión síncrona para cambios de diseño grandes.
- **SHOULD** que el autor se autorrevise el diff antes de pedir revisión.

## contract-testing

- **MUST** tener un contrato explícito y versionado por cada interfaz entre servicios: OpenAPI (REST), AsyncAPI/schema registry (eventos), `.proto` (gRPC).
- **MUST** verificar el contrato en CI en ambos lados: el proveedor demuestra que lo cumple; el consumidor demuestra qué usa.
- **MUST** elegir enfoque por caso: consumer-driven (Pact) cuando hay varios consumidores con necesidades distintas; schema-first con validación cuando el proveedor publica un contrato único.
- **MUST** que un cambio incompatible falle en el pipeline del proveedor antes de desplegar (ver `backward-compatibility-rules`).
- **SHOULD** que los stubs de consumidor (WireMock) se generen del contrato, no se escriban a mano.
- **SHOULD** probar eventos con compatibilidad de esquema (ver `schema-registry-and-evolution`).
- **MUST NOT** sustituir los contract tests por un E2E entre entornos compartidos.
- **MUST NOT** probar lógica de negocio en el contract test: solo forma, tipos y semántica de la interfaz.

## coverage-policy

- **MUST** medir cobertura con JaCoCo en el build Maven y publicar el informe en CI.
- **MUST** exigir un umbral mínimo en el `check` de JaCoCo: sugerido 80 % de líneas y 70 % de ramas en dominio y aplicación (valores por confirmar por proyecto).
- **MUST** aplicar la regla "el código nuevo no baja la cobertura": cobertura del diff mínima 80 % (gate del analizador usado).
- **MUST NOT** bajar el umbral para que pase el build sin ADR o decisión registrada.
- **MUST NOT** escribir tests sin aserciones para subir el número.
- **MUST** documentar las exclusiones (DTOs puros, configuración, `main`, clases generadas) en el pom, nunca con anotaciones ad hoc dispersas.
- **SHOULD** exigir más en dominio (lógica) que en adaptadores finos.
- **SHOULD** combinar con mutation testing en el dominio crítico.

## e2e-testing

- **MUST** limitar la suite e2e a flujos críticos (orientativo: decenas, no cientos) y mantener cada test independiente.
- **MUST** ejecutar contra un entorno efímero y reproducible (Docker Compose o Kubernetes local con Testcontainers/kind), con datos creados por el propio test.
- **MUST** usar selectores estables (`data-testid` o roles accesibles), no XPath frágil ni textos que cambian.
- **MUST** esperar condiciones (auto-wait del framework o Awaitility), nunca sleeps fijos.
- **MUST NOT** depender de servicios de terceros reales; sustituirlos por dobles (WireMock).
- **MUST NOT** compartir estado ni orden entre tests e2e.
- **MUST** guardar artefactos al fallar (captura, traza, vídeo, logs de servicios).
- **SHOULD** probar la API directamente cuando el flujo no necesita UI, y reservar la UI para lo que solo la UI puede romper.
- **SHOULD** aplicar `flaky-test-management` a cualquier test e2e inestable: se arregla o se elimina, no se reintenta a ciegas.
- **SHOULD** el frontend usar Playwright o Cypress según decisión del proyecto (comprobar versión y elección en la capa frontend).

## flaky-test-management

- **MUST** tratar un test flaky como defecto con dueño y fecha: abrir incidencia, asignar y fijar plazo (sugerido: 7 días).
- **MUST NOT** "arreglar" con reintentos globales (`rerunFailingTestsCount` en todo el build) ni con `Thread.sleep`.
- **MUST** esperar condiciones, no tiempo: Awaitility o latches/`CountDownLatch`.
- **MUST** controlar las fuentes de no determinismo: reloj inyectado (`Clock`), semillas, orden de colecciones, zonas horarias, puertos aleatorios, orden de ejecución.
- **MUST** aislar estado: sin datos compartidos entre tests, BD limpia por test, sin dependencia del orden.
- **MUST** poner en cuarentena un flaky con `@Disabled("FLAKY-123: motivo, fecha límite")` solo si hay incidencia enlazada.
- **SHOULD** medir la tasa de flakiness por test en CI y listar los peores.
- **SHOULD** reproducir localmente repitiendo el test (`@RepeatedTest`) o en bucle antes de corregir.

## integration-testing-testcontainers

- **MUST** probar contra la misma tecnología y versión mayor que producción (PostgreSQL real, no H2 como sustituto).
- **MUST** fijar la imagen con tag explícito, nunca `latest`; versión: comprobar según el estándar del proyecto.
- **MUST** que cada IT sea independiente: limpiar datos o usar transacciones/esquemas por test.
- **MUST** aplicar las migraciones reales (Flyway/Liquibase) en el contenedor; no `ddl-auto=create`.
- **SHOULD** usar `@ServiceConnection` (Spring Boot 3.1+) o `@DynamicPropertySource` para enlazar propiedades.
- **SHOULD** compartir un contenedor por suite (campo `static` o clase base) para no pagar el arranque por clase.
- **SHOULD** esperar con Awaitility, no con `sleep`, a efectos asíncronos (mensajes Kafka).
- **MUST NOT** depender de un servicio levantado a mano o de `docker compose` previo para pasar el IT.
- **MUST NOT** activar `reuse` en CI; solo como comodidad local opcional.

## localstack-aws

- **MUST** tratar LocalStack como emulador de API para tests de comportamiento del adaptador, nunca como evidencia de que funciona en AWS.
- **MUST** documentar en el test o README qué servicios se emulan y qué NO se reproduce (políticas IAM reales, SCP, cifrado KMS con claves reales, límites y throttling, eventual consistency real).
- **MUST** configurar el endpoint por propiedades (`endpointOverride`) solo en el perfil de test; el código de producción no conoce LocalStack.
- **MUST** usar credenciales falsas obvias (`example`/`changeme`) en el contenedor; nunca credenciales reales.
- **SHOULD** levantar LocalStack con Testcontainers (módulo LocalStack) y fijar la imagen con tag explícito.
- **SHOULD** limitar los servicios habilitados a los necesarios para acelerar el arranque.
- **MUST NOT** afirmar "probado en AWS" ni "listo para producción en AWS" por pasar tests en LocalStack; la fórmula es "preparado para AWS, no verificado en real" (ADR-0004).
- **MUST** tener en cuenta que desde el 2026-03-23 no existe la edición Community: la imagen requiere cuenta y auth token, y el plan gratuito es solo para uso no comercial (verificado el 2026-11-08, ver `aws-emulation`). En un proyecto corporativo su uso exige plan de pago y un ADR; preferir emuladores sin cuenta (DynamoDB Local, ElasticMQ, MinIO) cuando basten.
- **MUST NOT** depender de funcionalidades de pago de LocalStack por defecto (D16); si un test las requiere, es una decisión explícita y documentada.

## mutation-testing

- **MUST** usar PIT (`pitest-maven`) solo sobre paquetes de dominio, acotados con `targetClasses` y `targetTests`.
- **MUST** ejecutar PIT en CI nocturno o en PR sobre las clases modificadas (modo incremental), no en cada commit local.
- **MUST** fijar `mutationThreshold` para el módulo (inicio sugerido: 70) y subirlo gradualmente; no bajarlo para que pase el build.
- **MUST** tratar cada mutante superviviente como una de dos cosas: test que falta o código muerto/equivalente (documentarlo).
- **MUST NOT** perseguir 100 %: los mutantes equivalentes existen.
- **MUST NOT** usar la cobertura de líneas como sustituto: un test sin aserciones da cobertura y cero mutantes muertos.
- **SHOULD** excluir con `excludedClasses` generados (MapStruct), `toString` y logging.
- **SHOULD** usar `withHistory` / análisis incremental para reducir tiempos.

## performance-testing

- **MUST** definir antes de ejecutar los criterios de aceptación derivados del SLO (p95/p99, error rate, throughput) y la carga objetivo.
- **MUST** distinguir tipos: **baseline** (carga mínima de referencia), **load** (carga esperada), **soak** (carga sostenida horas: fugas, agotamiento de pool), **spike** (subida brusca y recuperación), **stress** (hasta romper).
- **MUST** ejecutar JMeter en modo no-GUI (`-n`) y guardar resultados `.jtl` y el informe HTML; el GUI solo para diseñar el plan.
- **MUST** correr con datos y volumen representativos y con calentamiento (warm-up) descartado del análisis.
- **MUST** comparar siempre contra el baseline anterior y registrar versión del código, entorno y configuración.
- **MUST NOT** apuntar la prueba a sistemas de terceros ni a entornos compartidos sin autorización.
- **MUST NOT** afirmar capacidad en AWS a partir de pruebas locales; indicar "preparado para AWS, no verificado en real".
- **SHOULD** medir también el cliente generador (CPU/red) para no confundir sus límites con los del servicio.
- **SHOULD** ejecutar un smoke de rendimiento en CI y las pruebas largas de forma programada.

## property-based-testing

- **MUST** formular la propiedad como invariante (ej. `decode(encode(x)) == x`), no como reimplementación de la función.
- **MUST** que el test sea reproducible: conservar la semilla que jqwik reporta al fallar y convertir el contraejemplo en un test por ejemplo.
- **MUST** acotar generadores al dominio válido (`@IntRange`, `@StringLength`, `Arbitraries`) en vez de filtrar con `assume` masivamente.
- **MUST NOT** usar aleatoriedad no controlada (`Math.random`, `UUID.randomUUID`) dentro de la propiedad.
- **SHOULD** complementar, no sustituir, los tests por ejemplo de casos de negocio conocidos.
- **SHOULD** mantener el número de intentos por defecto en CI local y subirlo solo en el job nocturno.
- **SHOULD** crear generadores reutilizables (`@Provide`) para tipos de dominio como `Money`.

## resilience-testing

- **MUST** tener un test por cada política de resiliencia declarada: timeout, número de reintentos, apertura y cierre del breaker, fallback.
- **MUST** simular el fallo de forma determinista: WireMock (`withFixedDelay`, `Fault`), Toxiproxy en Testcontainers (latencia, corte), o dobles que lanzan excepciones.
- **MUST** verificar el resultado observable: respuesta degradada correcta, código de error esperado, métricas del breaker, ausencia de efectos duplicados.
- **MUST** comprobar que los reintentos son idempotentes (ver `idempotency-keys`) y con backoff y jitter acotados.
- **MUST NOT** usar `Thread.sleep` para esperar el estado del breaker; usar Awaitility o reloj controlable.
- **MUST NOT** probar la política con timeouts reales largos: configurarlos pequeños en el perfil de test.
- **SHOULD** probar la recuperación (la dependencia vuelve y el breaker cierra).
- **SHOULD** cubrir apagado ordenado y reinicio de dependencia (ver `graceful-shutdown-lifecycle`).

## static-analysis

- **MUST** ejecutar en cada build, y fallar el build en el nivel acordado: Checkstyle (estilo), PMD (malas prácticas), SpotBugs (bugs de bytecode) y Error Prone (errores en compilación).
- **MUST** configurar los plugins una sola vez en el `pluginManagement` del parent POM (ver `parent-pom`) con ficheros de reglas versionados en el repo.
- **MUST** partir de reglas estrictas en código nuevo; la deuda previa se registra en un baseline explícito con plan, no con desactivación global.
- **MUST** que cada supresión (`@SuppressWarnings`, `@SuppressFBWarnings`, `// NOPMD`) lleve justificación en una línea y alcance mínimo.
- **MUST NOT** bajar la severidad o desactivar una regla para pasar un PR sin decisión registrada.
- **SHOULD** ejecutar las comprobaciones rápidas (Checkstyle, Error Prone) en cada compilación local y las pesadas (SpotBugs, PMD) en CI.
- **SHOULD** definir un quality gate: sin bugs nuevos, sin vulnerabilidades nuevas, cobertura sobre código nuevo según `coverage-policy`.
- **SHOULD** que la versión de cada herramienta quede fijada en el BOM/parent y actualizada por Renovate/Dependabot.

## tdd

- **MUST** escribir un test que falla (rojo) por la razón correcta antes de escribir código de producción.
- **MUST** ejecutar el test y ver el fallo; un test nunca visto fallar no prueba nada.
- **MUST** escribir el mínimo código para pasar (verde) y refactorizar solo con todo en verde.
- **MUST** que todo bug corregido incluya un test de regresión que falla antes del arreglo.
- **SHOULD** avanzar en pasos pequeños: un comportamiento por test, nombre que describe el comportamiento.
- **SHOULD** empezar por el caso más simple y añadir casos límite después (null, vacío, límites, duplicados).
- **MUST NOT** modificar el test para que pase cuando el fallo revela un defecto del código.
- **MUST NOT** probar detalles de implementación (métodos privados, orden interno de llamadas) en vez de comportamiento observable.

## test-data-management

- **MUST NOT** usar datos personales reales en tests ni en entornos no productivos; usar datos sintéticos o anonimizados (ver `pii-and-data-classification`).
- **MUST** crear los datos con builders / object mothers que expongan solo lo relevante para el test; el resto con valores por defecto válidos.
- **MUST** que cada test cree sus propios datos y no dependa de los de otro; aislamiento por transacción con rollback, truncado o contenedor nuevo.
- **MUST** que los identificadores sean únicos por ejecución (UUID o secuencia) para permitir ejecución en paralelo.
- **MUST NOT** compartir un dataset mutable global ("el cliente 1 de data.sql").
- **SHOULD** versionar fixtures grandes junto al test y mantenerlos mínimos.
- **SHOULD** generar volumen para rendimiento con scripts reproducibles (semilla fija), nunca copiando producción.
- **SHOULD** usar el esquema real (migraciones Flyway/Liquibase) para preparar la BD de test, no un DDL paralelo.

## test-strategy

- **MUST** seguir una pirámide: muchos tests unitarios rápidos, algunos de integración con dependencias reales, muy pocos E2E.
- **MUST** asignar cada test a una capa explícita por convención de nombre: `*Test` (unitario, Surefire) y `*IT` (integración, Failsafe).
- **MUST** que los tests unitarios no toquen red, disco ni reloj real y corran en segundos.
- **MUST** probar cada riesgo en la capa más barata que lo detecta (regla de negocio: unitario; mapeo SQL: integración con BD real; contrato entre servicios: contract test).
- **SHOULD** usar slices de Spring (`@WebMvcTest`, `@DataJpaTest`) antes que `@SpringBootTest` completo (ver `testing-slices`).
- **SHOULD** definir en el `README` del proyecto qué se ejecuta en cada fase: PR (unit + IT + estática), nightly (mutación, rendimiento corto), release (E2E, carga).
- **MUST NOT** compensar tests unitarios ausentes con E2E lentos.
- **MUST NOT** borrar o ignorar (`@Disabled`) un test para poner el build en verde sin ticket enlazado.

## unit-testing-java

- **MUST** usar JUnit 5 (Jupiter) y AssertJ; estructura Arrange-Act-Assert con un solo comportamiento por test.
- **MUST** nombrar el test por comportamiento: `rejectsOrder_whenStockIsInsufficient`.
- **MUST** inyectar por constructor para poder instanciar la clase sin Spring.
- **MUST** inyectar `Clock` y generadores de ids; nunca depender de `LocalDateTime.now()` ni `UUID.randomUUID()` directos.
- **MUST NOT** usar `Thread.sleep`; usar latches o Awaitility (ver `concurrency-testing`).
- **MUST NOT** mockear tipos que no son tuyos (JDK, cliente HTTP, `JdbcTemplate`) ni value objects; usar instancias reales.
- **SHOULD** preferir fakes en memoria de puertos propios frente a Mockito cuando haya varias interacciones.
- **SHOULD** usar `@ParameterizedTest` para tablas de casos; `@Nested` para agrupar contextos.
- **SHOULD** limitar `verify(...)` a efectos de salida relevantes (evento publicado, correo enviado), no a cada llamada interna.
- **MUST NOT** usar Lombok en tests ni en producción (D27).

## wiremock-and-stubbing

- **MUST** stubear por método, ruta y, cuando importe, cabeceras y cuerpo; evitar `anyUrl()` genérico.
- **MUST** probar caminos de fallo: 4xx, 5xx, cuerpo malformado, timeout, conexión cortada (`Fault`), respuesta lenta.
- **MUST** verificar las peticiones enviadas (`verify`) cuando la salida es el comportamiento (cabecera de auth, idempotency key, cuerpo).
- **MUST** usar puerto dinámico y enlazar la URL base por propiedad; nunca puerto fijo.
- **MUST** resetear stubs entre tests (extensión JUnit 5 de WireMock o `resetAll`).
- **SHOULD** derivar los stubs de la especificación OpenAPI/contrato cuando exista, para que no diverjan.
- **SHOULD** usar escenarios con estado (`scenarios`) para probar reintentos (primero 503, luego 200).
- **MUST NOT** hacer que los tests unitarios dependan de WireMock (es de integración).
- **MUST NOT** guardar en los stubs datos reales de producción ni tokens reales.
