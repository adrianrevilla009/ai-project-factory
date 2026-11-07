# Estándares · 05-architecture

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## anti-corruption-layer

- **MUST** aislar el modelo ajeno en un paquete `adapter.out.<system>`; nada fuera de él importa sus tipos.
- **MUST** traducir en la ACL (traductor/mapper) a tipos del dominio propio; los DTO externos no cruzan la frontera.
- **MUST** exponer el sistema externo mediante un puerto del dominio con lenguaje propio (`CustomerDirectory`, no `LegacyCrmClient`).
- **MUST** gestionar en la ACL errores, timeouts y formatos raros del externo, devolviendo errores de dominio.
- **SHOULD** testear el traductor con casos reales anonimizados del sistema externo.
- **SHOULD** que la ACL sea la única parte que cambia cuando el externo cambia.
- **MUST NOT** reutilizar clases generadas (WSDL/OpenAPI del tercero) en el dominio o la aplicación.

## bff-and-api-gateway

- **MUST** que el API gateway sólo haga preocupaciones transversales: enrutado, TLS, autenticación/validación de token, rate limiting, CORS, observabilidad.
- **MUST NOT** poner lógica de negocio en el gateway.
- **MUST** que un BFF pertenezca al equipo del cliente al que sirve y agregue/adapte datos para ese cliente.
- **MUST NOT** compartir un único BFF entre clientes con necesidades divergentes.
- **MUST** que el BFF delegue las reglas de negocio en los servicios; es adaptación, no dominio.
- **MUST** propagar identidad y cabeceras de trazado (`traceparent`) aguas abajo y aplicar timeouts y circuit breaker en las llamadas.
- **SHOULD** que la autorización fina siga en cada servicio (defensa en profundidad), no solo en el gateway.
- **SHOULD** versionar la API pública y gestionar su ciclo de vida en el gateway (`api-versioning-deprecation`).

## cell-based-architecture

- **MUST** definir la celda como unidad completa e independiente (cómputo, datos, colas) que sirve a un subconjunto de clientes.
- **MUST** que no haya dependencias síncronas entre celdas ni estado compartido en la ruta crítica.
- **MUST** un enrutador de celdas muy simple y sin estado complejo, dueño de la asignación cliente -> celda.
- **MUST** dimensionar la celda con un tamaño máximo conocido y añadir celdas para crecer, no agrandarlas.
- **MUST** poder desplegar y revertir por celda (canary por celda).
- **SHOULD** observabilidad y alertas por celda con etiqueta `cell_id`.
- **SHOULD** definir qué datos son globales (catálogo, identidad) y cómo se replican de forma asíncrona.
- **MUST NOT** introducir doble escritura entre celdas; cada dato tiene una celda dueña.

## clean-architecture

- **MUST** que las dependencias de código fuente apunten solo hacia dentro: frameworks/adaptadores -> casos de uso -> entidades.
- **MUST** que las entidades y casos de uso no conozcan HTTP, SQL, Kafka ni el contenedor de Spring.
- **MUST** pasar datos entre fronteras como estructuras simples (`record`), no entidades JPA ni objetos de framework.
- **MUST** que cada caso de uso tenga una intención única (`CancelOrder`), no servicios "Manager" genéricos.
- **SHOULD** que el `main`/configuración Spring sea el único lugar que conoce todas las implementaciones (composición).
- **SHOULD** limitar el número de círculos al necesario (entidades, casos de uso, adaptadores); no crear capas vacías.
- **MUST NOT** introducir una capa solo para delegar (`ServiceImpl` que llama a otro `Service` sin lógica).

## code-smells-and-refactoring

- **MUST** tener tests que pasan (caracterización si faltan) antes de refactorizar.
- **MUST** hacer refactors en pasos pequeños, con tests en verde entre pasos, separados de los cambios de comportamiento (commits distintos).
- **MUST** tratar como olores a corregir: método largo, clase dios, parámetros en cascada, `Feature Envy`, duplicación, primitive obsession, switch sobre tipo, comentarios que explican código confuso.
- **SHOULD** aplicar la regla de los scouts: dejar el código tocado un poco mejor, con alcance acotado.
- **SHOULD** refactorizar con las herramientas del IDE (extract method, rename) antes que a mano.
- **MUST NOT** mezclar refactor y funcionalidad en el mismo commit.
- **MUST NOT** "arreglar" olores mediante supresiones de análisis estático sin justificar.
- **SHOULD** registrar olores no abordables como deuda (`tech-debt-management`).

## connascence-and-coupling

- **MUST** evaluar cada dependencia por fuerza, grado y localidad: acoplamiento fuerte solo si los elementos están cerca (mismo módulo/equipo).
- **MUST** convertir connascence fuerte a débil al cruzar fronteras: de nombre/tipo (estática) a contrato explícito; evitar de ejecución, temporalidad y valor entre servicios.
- **MUST NOT** compartir entre contexts clases de dominio, entidades JPA ni esquemas de BD (ver `ddd-strategic`).
- **MUST NOT** crear ciclos de dependencia entre paquetes o módulos.
- **SHOULD** preferir duplicar un DTO pequeño entre servicios antes que una librería compartida que obligue a desplegar a la vez.
- **SHOULD** reducir parámetros posicionales y literales mágicos (connascence de posición y de significado) con tipos y enums.
- **SHOULD** considerar acoplamiento temporal en llamadas síncronas en cadena; evaluar asincronía (ver `event-driven`).
- **SHOULD** registrar en ADR los acoplamientos fuertes aceptados y su razón.

## consistency-and-cap-tradeoffs

- **MUST** decidir la consistencia por caso de uso, no globalmente: qué operaciones requieren lectura fuerte (saldo, stock vendible) y cuáles toleran retraso (listados, contadores).
- **MUST** mantener ACID dentro de una frontera transaccional (un aggregate, una BD) y consistencia eventual entre fronteras.
- **MUST** documentar en el ADR el comportamiento ante partición: qué se sacrifica (disponibilidad o consistencia) en cada operación.
- **MUST** tratar la lectura desde réplica o caché como potencialmente obsoleta; si el flujo lee tras escribir, leer del primario o usar token de versión.
- **MUST NOT** presentar CAP como "elige 2 de 3": la partición no es opcional; la elección real es consistencia vs disponibilidad durante la partición, y latencia vs consistencia el resto del tiempo (PACELC).
- **MUST** usar claves de idempotencia en operaciones de escritura reintentables.
- **SHOULD** usar bloqueo optimista (`@Version`) para conflictos de escritura concurrente.
- **SHOULD** declarar la ventana máxima aceptable de obsolescencia (ej. proyecciones < 5 s) como requisito medible.
- **SHOULD** declarar qué no se reproduce en local (multi-AZ, replicación asíncrona real, latencias entre regiones); preparado para AWS, no verificado en real.

## cqrs

- **MUST** separar comandos (cambian estado, no devuelven datos de negocio) de consultas (no cambian estado) a nivel de código: handlers distintos.
- **MUST** justificar en un ADR el paso a modelo de lectura separado (carga, forma, latencia); el nivel mínimo es misma BD con proyecciones/vistas.
- **MUST NOT** hacer doble escritura Postgres + NoSQL desde el comando (decisión 4.5); la proyección se alimenta desde eventos publicados con outbox o desde CDC.
- **MUST** tratar el modelo de lectura como derivado y reconstruible desde la fuente de verdad.
- **MUST** diseñar la UI y la API para consistencia eventual cuando la proyección sea asíncrona (mostrar estado pendiente, no asumir lectura inmediata).
- **SHOULD** empezar por el nivel 1 (mismo esquema, consultas con DTO/proyecciones) y subir solo con evidencia.
- **SHOULD** hacer proyecciones idempotentes (reaplicar un evento no cambia el resultado).
- **MUST NOT** devolver entidades JPA desde consultas; usar DTO de lectura.

## ddd-strategic

- **MUST** identificar subdominios (core, supporting, generic) y concentrar el esfuerzo de diseño en el core.
- **MUST** definir cada bounded context con nombre, responsabilidad, lenguaje ubicuo propio y dueño (equipo).
- **MUST** documentar el context map: para cada relación indicar el patrón (Customer/Supplier, Conformist, Anti-Corruption Layer, Shared Kernel, Open Host Service/Published Language).
- **MUST NOT** compartir el modelo de dominio ni el esquema de BD entre contexts; se integran por contratos (API o eventos).
- **MUST NOT** usar un único modelo "canónico" de empresa para todos los contexts.
- **SHOULD** alinear un bounded context con un módulo (monolito modular) o un servicio, nunca varios contexts en un mismo módulo.
- **SHOULD** comprar/adoptar solución estándar para subdominios genéricos (identidad con Keycloak, D-decisiones del repo) en lugar de modelarlos.
- **SHOULD** usar Event Storming para descubrir contexts; el resultado se guarda como ADR o documento de arquitectura.

## ddd-tactical

- **MUST** modelar un aggregate con una única raíz; todo cambio pasa por métodos de la raíz que protegen invariantes.
- **MUST** referenciar otros aggregates solo por identidad (`CustomerId`), nunca por referencia de objeto.
- **MUST** modificar un solo aggregate por transacción; la coordinación entre aggregates va por eventos de dominio (ver `event-driven`, `sagas-and-process-managers`).
- **MUST** usar value objects inmutables (records Java) para conceptos sin identidad: `Money`, `Email`, `Quantity`.
- **MUST NOT** exponer setters públicos en entidades; los estados se cambian con verbos del lenguaje ubicuo.
- **MUST NOT** depender de Spring, JPA ni de infraestructura desde el paquete `domain`.
- **MUST NOT** usar Lombok (D27); usar records y código explícito.
- **SHOULD** definir un repositorio por aggregate root, con interfaz en `domain` e implementación en `infrastructure`.
- **SHOULD** mantener aggregates pequeños; si una colección crece sin límite, es otro aggregate.
- **SHOULD** usar servicios de dominio solo cuando la lógica no pertenece a ninguna entidad.

## event-driven

- **MUST** distinguir evento (hecho pasado, `OrderPlaced`) de comando (petición, `ReserveStock`); el evento no espera respuesta.
- **MUST** publicar mediante outbox transaccional: el cambio de estado y el evento se guardan en la misma transacción; un relay los envía. Sin dual write a la BD y al broker.
- **MUST** asumir entrega al-menos-una-vez: consumidores idempotentes (tabla de mensajes procesados o upsert natural).
- **MUST** versionar y documentar el contrato del evento (esquema, campos obligatorios); cambios compatibles hacia atrás.
- **MUST** configurar reintentos con backoff y una dead-letter queue con alerta.
- **MUST NOT** asumir orden global; solo se garantiza dentro de una clave/partición.
- **MUST NOT** incluir en el evento el modelo interno completo; publicar lo que el consumidor necesita (o un id para consultar).
- **SHOULD** incluir `eventId`, `occurredAt`, `type`, `version` y `correlationId` en el sobre.
- **SHOULD** tener brokers locales equivalentes funcionales para desarrollo; qué NO se reproduce en local respecto a AWS (políticas IAM, cuotas, latencias reales de SQS/SNS/MSK) debe declararse en la matriz AWS-local. Preparado para AWS, no verificado en real.

## event-sourcing

- **MUST** documentar en un ADR por qué una tabla de auditoría o el historial CDC no basta.
- **MUST** tratar los eventos como inmutables y en pasado (`OrderPlaced`); la corrección se hace con un evento compensatorio, nunca editando.
- **MUST** versionar el esquema de eventos y escribir upcasters para eventos antiguos antes de cambiar su forma.
- **MUST** garantizar concurrencia optimista por stream (versión esperada al añadir eventos).
- **MUST** usar snapshots solo como optimización reconstruible, nunca como fuente de verdad.
- **MUST NOT** guardar el mismo estado además en una segunda tabla escrita por el comando (sin doble escritura); las vistas son proyecciones derivadas (ver `cqrs`).
- **MUST NOT** guardar datos personales directamente en eventos inmutables sin estrategia de borrado (cifrado por sujeto o referencias); consultar normativa vigente, borrador por confirmar con fuente oficial.
- **SHOULD** limitar los streams por aggregate (ver `ddd-tactical`).

## evolutionary-architecture-fitness-functions

- **MUST** convertir cada característica arquitectónica priorizada (ver `quality-attributes-atam`) en al menos una fitness function ejecutable o declarar "revisión humana".
- **MUST** ejecutar las fitness functions en CI y que un fallo bloquee el merge (no solo informe).
- **MUST** dar a cada una un dueño, un umbral explícito y un mensaje de error que indique cómo corregir.
- **MUST** versionar las fitness functions junto al código, y evolucionarlas con ADR cuando cambie la decisión.
- **SHOULD** combinar tipos: estructurales (ArchUnit, dependency-cruiser), de rendimiento (test de carga con umbral), de seguridad (escáner de dependencias) y de datos (migraciones compatibles).
- **SHOULD** empezar con pocas (3-5) de alto valor y ampliar por incidentes reales.
- **SHOULD** preferir cambios incrementales guiados por estas reglas antes que reescrituras.
- **MUST NOT** desactivar una fitness function para "pasar el build"; se corrige el código o se enmienda la decisión mediante ADR.
- **MUST NOT** afirmar cumplimiento de características de despliegue AWS solo por pasar tests locales; preparado para AWS, no verificado en real.

## gof-patterns-in-practice

- **MUST** poder enunciar el problema concreto que resuelve el patrón (en el PR o comentario) antes de introducirlo.
- **SHOULD** usar Strategy con interfaces funcionales o `Map<Key, Handler>` en lugar de cadenas de `if/else` o `switch` que crecen.
- **SHOULD** usar Factory/builder para construcción compleja; para objetos de valor, `record` con validación en el constructor compacto.
- **SHOULD** usar Decorator (o AOP de Spring) para preocupaciones transversales; evitar herencia para ello.
- **MUST NOT** implementar Singleton manual; usar el ámbito de bean de Spring y evitar estado mutable compartido.
- **MUST NOT** usar Service Locator ni `ApplicationContext.getBean` en código de negocio.
- **SHOULD** preferir Observer vía eventos de Spring/dominio (`domain-events-in-spring`) a listeners manuales.
- **MUST NOT** nombrar clases por el patrón si no aportan semántica (`OrderFactoryImpl`, `StrategyManager`).

## hexagonal

- **MUST** separar paquetes `domain`, `application` y `adapter` (`adapter.in.web`, `adapter.out.persistence`...).
- **MUST** que `domain` no importe Spring, JPA, Jackson ni nada de `adapter`.
- **MUST** definir los puertos de salida (`OrderRepository`, `PaymentGateway`) como interfaces en `application` o `domain`; los adaptadores los implementan.
- **MUST** exponer casos de uso como puertos de entrada (`PlaceOrderUseCase`) invocados por los adaptadores de entrada.
- **MUST NOT** devolver entidades JPA ni DTOs HTTP desde el dominio; mapear en el adaptador.
- **SHOULD** una entidad JPA separada del modelo de dominio cuando el modelo de persistencia distorsione el dominio; aceptar la entidad como modelo solo en servicios simples y decidirlo por escrito.
- **SHOULD** que los tests del dominio no necesiten contexto Spring.
- **MUST NOT** usar Lombok (D27); usar `record` y constructores explícitos.

## layering-rules-archunit

- **MUST** codificar la arquitectura elegida como tests ArchUnit que fallen el build (`mvn verify`).
- **MUST** incluir al menos: regla de capas, ausencia de ciclos entre paquetes/módulos y dominio sin dependencias de framework.
- **MUST** usar `@AnalyzeClasses(packages = ...)` acotado al paquete base, excluyendo tests si procede.
- **MUST NOT** relajar una regla para que pase el build: corregir el código o abrir una decisión (ADR) que cambie la regla.
- **SHOULD** usar `consideringOnlyDependenciesInLayers()` para no ahogar la regla en dependencias de librerías.
- **SHOULD** nombrar cada regla por la intención (`domain_does_not_depend_on_frameworks`).
- **SHOULD** usar `FreezingArchRule` solo para adoptar reglas en código heredado, con plan de descongelado.
- **MUST** fijar la versión de `archunit-junit5` en el BOM del proyecto (TODO-VERIFY versión vigente).

## microservices-decision-guide

- **MUST** partir de `modular-monolith` salvo que haya un motivo medible documentado.
- **MUST** justificar cada servicio con al menos un motivo: escalado distinto, cadencia de despliegue independiente, aislamiento de fallos/seguridad, o autonomía de un equipo.
- **MUST** que el servicio sea dueño de sus datos; sin base de datos compartida entre servicios y sin doble escritura Postgres+NoSQL.
- **MUST** registrar la decisión en un ADR con alternativas y coste operativo asumido (observabilidad, CI/CD, contratos, consistencia eventual).
- **MUST NOT** crear servicios por capa técnica ni "nano-servicios" que siempre se despliegan juntos.
- **MUST NOT** introducir llamadas síncronas en cadena sin timeouts, reintentos acotados y circuit breaker.
- **SHOULD** exigir contratos versionados (OpenAPI/AsyncAPI) y contract tests antes de la primera integración.
- **SHOULD** que un servicio sea operable por un único equipo.

## modular-monolith

- **MUST** dividir por capacidad de negocio (`orders`, `billing`), no por capa técnica.
- **MUST** que cada módulo exponga una API pública (interfaz/paquete `api`) y oculte su interior (`internal`).
- **MUST NOT** acceder a tablas o repositorios de otro módulo; comunicar por API del módulo o eventos de dominio.
- **MUST NOT** hacer joins SQL ni claves foráneas entre esquemas de módulos distintos.
- **MUST** que no haya ciclos entre módulos.
- **SHOULD** un esquema (o prefijo de tablas) por módulo en la misma base de datos, con propiedad clara.
- **SHOULD** comunicar efectos secundarios entre módulos con eventos internos (ver `domain-events-in-spring`).
- **MAY** usar Spring Modulith para verificar y documentar módulos (TODO-VERIFY versión y API).

## multi-tenant-architecture

- **MUST** decidir el modelo de aislamiento en un ADR: base por tenant, esquema por tenant o tabla compartida con `tenant_id` (silo, bridge, pool), según riesgo, coste y número de tenants.
- **MUST** derivar el tenant de una fuente confiable (claim del token validado, ej. Keycloak realm/claim), nunca de un parámetro o cabecera que controle el cliente.
- **MUST** propagar el tenant en un contexto de petición (hilo, mensajes, logs, trazas) y limpiarlo al terminar.
- **MUST** aplicar el filtro de tenant en un único punto central (filtro de Hibernate, Row Level Security de Postgres o repositorio base), no en cada consulta a mano.
- **MUST** incluir `tenant_id` en claves de caché, claves de objeto, topics/claves de mensajes e índices únicos.
- **MUST** testear aislamiento: un test que cree datos en el tenant A y verifique que B no los ve por ninguna vía.
- **SHOULD** aplicar cuotas y rate limiting por tenant para evitar "vecino ruidoso".
- **SHOULD** usar Row Level Security como defensa en profundidad además del filtro de aplicación.
- **MUST NOT** usar un usuario de BD con `BYPASSRLS` en la aplicación.
- **MUST NOT** mezclar datos de tenants en logs sin etiquetar el tenant.

## quality-attributes-atam

- **MUST** expresar cada atributo de calidad relevante como escenario medible: estímulo, entorno, respuesta y medida (p95 < 300 ms al 70 % de carga).
- **MUST** priorizar los escenarios (impacto de negocio x dificultad) y limitarse a los 3-5 que condicionan la arquitectura.
- **MUST** documentar los puntos de sensibilidad, los compromisos (trade-offs) y los riesgos de cada decisión en un ADR.
- **MUST** vincular cada escenario crítico con una verificación: prueba de carga, fitness function o prueba de resiliencia.
- **SHOULD** involucrar a negocio, operaciones y seguridad en la priorización.
- **MUST NOT** declarar atributos sin cifra ("rápido", "escalable", "seguro").
- **MUST NOT** afirmar cumplimiento de disponibilidad en AWS sin medición real: "preparado para AWS, no verificado en real".
- **SHOULD** revisar los escenarios cuando cambie el contexto.

## sagas-and-process-managers

- **MUST NOT** usar transacciones distribuidas (2PC/XA) entre servicios.
- **MUST** definir para cada paso su acción compensatoria (o declarar explícitamente que es irreversible y colocarlo el último).
- **MUST** persistir el estado de la saga (id, paso actual, estado, deadline) para sobrevivir a reinicios.
- **MUST** hacer cada paso y cada compensación idempotentes, con reintentos y backoff.
- **MUST** definir timeouts y estado terminal (`COMPLETED`, `COMPENSATED`, `FAILED_NEEDS_MANUAL`) con alerta en el último.
- **MUST** correlacionar todos los mensajes con `sagaId`/`correlationId`.
- **SHOULD** elegir coreografía (eventos) para 2-3 participantes y orquestación (process manager explícito) para flujos más largos o con ramas.
- **SHOULD** ordenar los pasos: primero los reversibles, al final el que no se puede deshacer (ej. cobro tras reservar stock).
- **SHOULD** exponer el estado de la saga a la UI/API (consistencia eventual, ver `consistency-and-cap-tradeoffs`).

## scalability-patterns

- **MUST** fijar objetivos numéricos (RPS, p95/p99, volumen de datos) antes de elegir patrones; sin número no hay decisión.
- **MUST** mantener los servicios stateless: la sesión y el estado viven en BD, caché externa o token, no en memoria del proceso.
- **MUST** medir antes de optimizar (profiling, métricas, test de carga) e identificar el cuello de botella real, normalmente la BD.
- **MUST** poner timeouts, límites de pool y de cola en toda llamada saliente; las colas deben estar acotadas.
- **MUST** aplicar backpressure o rechazo controlado (429/503 con `Retry-After`) en lugar de aceptar trabajo ilimitado.
- **MUST** definir TTL e invalidación para cada caché y tratar el fallo de caché como degradación, no como caída.
- **SHOULD** escalar primero verticalmente y con índices/consultas (ver bloque de persistencia), después réplicas de lectura, después particionado.
- **SHOULD** mover trabajo no interactivo a colas asíncronas (ver `event-driven`).
- **SHOULD** elegir la clave de partición por patrón de acceso y evitar claves calientes.
- **MUST NOT** escalar réplicas sin comprobar que el pool de conexiones de la BD lo soporta (réplicas x pool <= máximo de conexiones).

## solid

- **MUST** (SRP) que una clase tenga una sola razón para cambiar; separar reglas de negocio, persistencia y formato.
- **SHOULD** (OCP) extender comportamiento con composición/estrategias donde ya haya variación real, no por anticipación.
- **MUST** (LSP) que una subclase respete el contrato de la base (precondiciones no más fuertes, postcondiciones no más débiles); si lanza `UnsupportedOperationException`, el diseño es erróneo.
- **MUST** (ISP) interfaces pequeñas orientadas al cliente; no obligar a implementar métodos sin uso.
- **MUST** (DIP) depender de abstracciones en la frontera del dominio y usar inyección por constructor.
- **SHOULD** preferir composición sobre herencia.
- **MUST NOT** crear una interfaz por cada clase si solo hay una implementación y no es una frontera.
- **MUST NOT** usar inyección por campo (`@Autowired` en atributos); constructor explícito, sin Lombok (D27).

## strangler-fig-migration

- **MUST** introducir una fachada/proxy (gateway, ingress) delante del legado para poder redirigir por ruta o capacidad.
- **MUST** migrar por rebanadas verticales pequeñas y reversibles, una capacidad cada vez.
- **MUST** poder volver atrás (feature flag o regla de enrutado) en cada rebanada.
- **MUST** tener un dueño de datos por rebanada: sin doble escritura Postgres+NoSQL; si hace falta sincronizar, usar CDC/eventos con un único escritor.
- **MUST** proteger el modelo nuevo con `anti-corruption-layer`.
- **SHOULD** ejecutar en paralelo (shadow traffic o comparación de respuestas) antes de cortar tráfico.
- **MUST** definir y ejecutar la retirada del legado; una migración sin apagado final es deuda.
- **MUST NOT** añadir funcionalidad nueva al legado salvo corrección crítica.

## tech-debt-management

- **MUST** registrar cada deuda aceptada de forma explícita: qué es, por qué se acepta, impacto (interés), coste estimado de pago, dueño y fecha de revisión.
- **MUST** enlazar la deuda a código con un marcador rastreable (`TODO(DEBT-123)`), nunca un `TODO` anónimo.
- **MUST** distinguir deuda deliberada (decisión) de accidental (descubierta); la accidental se registra al detectarla.
- **MUST NOT** aceptar como deuda lo que compromete seguridad, integridad de datos o requisitos legales; eso se corrige antes de entregar.
- **MUST** priorizar por interés (frecuencia de cambio x fricción) y riesgo, no por antigüedad ni por molestia personal.
- **SHOULD** reservar capacidad fija recurrente al pago de deuda (ej. 10-20 % por iteración; valor de partida a calibrar por equipo).
- **SHOULD** pagar deuda junto a cambios funcionales en la misma zona (regla del boy scout) usando refactor seguro con tests (ver `code-smells-and-refactoring`).
- **SHOULD** revisar el registro en cada fase/gate y cerrar o reclasificar elementos caducados.
- **SHOULD** vigilar tendencias (tiempo de build, cobertura de módulos críticos, ciclos, dependencias obsoletas) como señales, no como objetivos en sí.

## twelve-factor

- **MUST** mantener un repositorio por servicio desplegable y un artefacto inmutable (imagen) promovido entre entornos (build, release, run separados).
- **MUST** declarar dependencias explícitamente en `pom.xml`; sin dependencias del sistema implícitas.
- **MUST** externalizar la configuración por entorno (variables de entorno, `ConfigMap`, secret manager); el mismo artefacto sirve a todos los entornos.
- **MUST NOT** guardar secretos en el repositorio ni en la imagen; solo referencias o valores `changeme`/`example` en ejemplos.
- **MUST** tratar servicios de apoyo (BD, broker, caché) como recursos adjuntos configurables por URL.
- **MUST** ser stateless y no compartir nada entre procesos salvo servicios de apoyo; el disco local es efímero.
- **MUST** escribir logs a stdout/stderr en formato estructurado (JSON); la plataforma los enruta.
- **MUST** soportar arranque rápido y apagado ordenado (SIGTERM, `server.shutdown=graceful`).
- **SHOULD** mantener paridad dev/prod: mismas versiones de Postgres, broker, etc. en local con contenedores; declarar lo que no se reproduce (servicios gestionados de AWS, IAM, redes). Preparado para AWS, no verificado en real.
- **SHOULD** tratar tareas administrativas (migraciones) como procesos puntuales (Job/Flyway al desplegar), no como parte oculta del arranque de todas las réplicas.
- **SHOULD** exponer el puerto por configuración (`server.port=${PORT:8080}`).
