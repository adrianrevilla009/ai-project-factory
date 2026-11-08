# Estándares · 22-polyglot-persistence

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## aggregates-and-event-design

- **MUST** un stream por agregado; el agregado es el límite de consistencia y de concurrencia (versión esperada).
- **MUST** nombrar eventos en pasado y con lenguaje del dominio (`PolicyIssued`, no `PolicyUpdated`).
- **MUST** hacer los eventos inmutables y autosuficientes para el negocio (`record` en Java, sin Lombok).
- **MUST** separar comando (intención, puede rechazarse) de evento (hecho, no se rechaza): `decide(state, command) -> events`, `evolve(state, event) -> state`.
- **MUST** mantener `evolve` puro, sin I/O, reloj ni aleatoriedad; el tiempo y los ids entran en el evento.
- **MUST** incluir `eventId`, `aggregateId`, `version`, `occurredAt`, `correlationId`, `causationId`, `schemaVersion`.
- **MUST NOT** guardar en el evento el estado completo "por comodidad" ni referencias a otros agregados que deban leerse para interpretarlo.
- **MUST NOT** guardar datos personales sin estrategia de supresión (`gdpr-and-immutable-events`).
- **SHOULD** mantener los streams acotados (si crecen sin fin, diseñar cierre del ciclo de vida o snapshots).
- **SHOULD** corregir con eventos compensatorios (`PaymentReversed`), nunca editando.

## audit-trail-without-event-sourcing

- **MUST** elegir la opción más simple que cumpla: (1) tabla `*_audit` escrita en la misma transacción; (2) Hibernate Envers; (3) CDC a un almacén de auditoría de solo-anexar; (4) tablas temporales si el motor las ofrece.
- **MUST** registrar actor (`user_id` o servicio), instante, acción, entidad e id, y diff o valores antes/después.
- **MUST** escribir la auditoría en la misma transacción que el cambio (o vía CDC del WAL); NUNCA como segundo paso best-effort.
- **MUST** que la tabla de auditoría sea de solo-anexar: sin `UPDATE`/`DELETE` para el rol de la aplicación.
- **MUST NOT** copiar PII completa al historial sin política de retención y borrado (ver `gdpr-and-immutable-events`, `retention-and-cleanup`).
- **SHOULD** particionar por fecha para poder archivar (ver `partitioning-and-archival`).
- **SHOULD** documentar en ADR por qué no se usa event sourcing.

## cache-strategies

- **MUST** usar cache-aside por defecto: leer caché, si falla leer la fuente y poblar; la escritura va a la fuente y luego invalida (`DEL`) la clave.
- **MUST** poner TTL a toda clave de caché; sin TTL, un bug de invalidación se vuelve permanente.
- **MUST** configurar `maxmemory` y `maxmemory-policy` explícitos; para caché pura `allkeys-lru` es un buen defecto según la documentación de Redis. `noeviction` devuelve error al llenarse.
- **MUST** que la aplicación funcione (más lenta) si Redis cae: timeout corto y degradación a la fuente (ver `resilience`).
- **MUST** prevenir stampede en claves calientes: TTL con jitter y bloqueo/single-flight por clave al regenerar.
- **MUST** prefijar claves con servicio, entidad y versión de esquema (`orders:v2:{id}`) y, si hay multi-tenant, el tenant (ver `multi-tenancy`).
- **MUST NOT** cachear datos personales sin TTL acotado y sin contemplar su borrado (ver `gdpr-and-immutable-events`).
- **MUST NOT** usar la misma instancia Redis para caché evictable y para datos persistentes (las políticas `volatile-*` lo permiten pero la documentación recomienda instancias separadas).
- **SHOULD** medir hit ratio (`keyspace_hits` / (`keyspace_hits` + `keyspace_misses`)) y `evicted_keys`.

## consistency-and-sagas

- **MUST** preferir diseñar para que el invariante viva dentro de un solo aggregate/datastore (transacción local) antes de recurrir a una saga.
- **MUST NOT** usar dos escrituras directas a datastores distintos en un mismo método esperando atomicidad (sin doble escritura Postgres+NoSQL, 4.5); usar `outbox-and-cdc`.
- **MUST** que cada paso de la saga sea idempotente y tenga una compensación definida (o una justificación escrita de por qué no es compensable).
- **MUST** persistir el estado de la saga (id, paso actual, deadline) para sobrevivir a reinicios, y definir timeouts y estado terminal `FAILED`/`COMPENSATED`.
- **MUST** documentar la ventana de inconsistencia aceptada y qué ve el usuario durante ella.
- **SHOULD** usar transacciones nativas cuando el alcance es un solo almacén: DynamoDB `TransactWriteItems` agrupa hasta 100 acciones y 4 MB, en una región y cuenta; no son válidas entre regiones de una global table.
- **SHOULD** reintentar con `ClientRequestToken` en DynamoDB: es válido 10 minutos tras terminar la petición; pasado ese tiempo se trata como nueva.
- **MUST NOT** usar 2PC/XA entre almacenes heterogéneos como solución por defecto.

## cqrs-read-models-and-search

- **MUST** que la fuente de verdad sea una sola (Postgres o DynamoDB); OpenSearch es una proyección derivada y reconstruible. Sin doble escritura Postgres+NoSQL desde el comando (4.5).
- **MUST** alimentar el índice desde `outbox-and-cdc` (eventos o CDC) con un indexador idempotente: documento con `_id` = id de negocio y versión externa para descartar eventos antiguos.
- **MUST** poder reindexar todo desde la fuente (alias + índice versionado `products_v2`, conmutar el alias al terminar; ver `rebuilds-and-replays`).
- **MUST** que la UI/API acepte consistencia eventual: tras escribir, la búsqueda puede tardar en reflejar; leer-tu-escritura se resuelve consultando la fuente por id.
- **MUST NOT** usar el índice de búsqueda como fuente de verdad ni para validaciones de negocio (unicidad, saldos).
- **MUST NOT** guardar datos que el usuario no debería ver: aplicar el filtrado de autorización/tenant también en la consulta de búsqueda (ver `multi-tenancy`).
- **SHOULD** definir mappings explícitos (no dynamic mapping abierto) y versionarlos en el repo.
- **SHOULD** vigilar el lag de indexación y exponerlo como métrica.

## data-sync-pitfalls

- **MUST** declarar un único dueño (fuente de verdad) por dato; el resto son derivados reconstruibles. Sin doble escritura Postgres+NoSQL (4.5).
- **MUST** asumir entrega al-menos-una-vez y fuera de orden entre claves: handlers idempotentes y con versión/secuencia (descartar si `incoming.version <= stored.version`).
- **MUST** tratar el borrado explícitamente: propagar tombstones/eventos de borrado; un `upsert` ciego deja "zombis".
- **MUST** tener un job de reconciliación periódico (conteos, checksums por rango) y un procedimiento de resincronización completa.
- **MUST** monitorizar lag y antigüedad del evento más viejo sin procesar, con alerta.
- **MUST** dimensionar el relay para su ventana de retención: DynamoDB Streams guarda 24 h; si el consumidor está caído más tiempo hay pérdida y se requiere resincronización completa desde la tabla. Kinesis Data Streams for DynamoDB admite retención de hasta 1 año.
- **MUST NOT** asumir atomicidad ni orden entre ítems en Streams: los registros de una misma transacción pueden llegar en momentos distintos e intercalados.
- **MUST NOT** sincronizar con "dual write + reintento" ni con triggers que llaman a sistemas externos dentro de la transacción.
- **SHOULD** versionar el esquema del evento de sincronización (ver `schema-registry-and-evolution`).
- **SHOULD** usar zona horaria UTC y `Instant` para marcas de tiempo; no resolver conflictos con relojes de pared salvo documentarlo.

## datastore-selection-guide

- **MUST** partir de PostgreSQL (Aurora PostgreSQL en AWS) como almacén por defecto del estado (ADR-0013).
- **MUST** asignar a cada agregado UNA única fuente de verdad y anotarla en el ADR o en el mapa de datos del proyecto.
- **MUST** justificar por escrito cada almacén adicional: patrón de acceso que Postgres no cubre, volumen o latencia medidos o estimados, y coste operativo asumido (`polyglot-operations-cost`).
- **MUST NOT** escribir el mismo agregado a la vez en Postgres y en un almacén NoSQL desde el comando (doble escritura: no es atómica). Los otros almacenes son proyecciones derivadas de eventos u outbox.
- **SHOULD** usar DynamoDB solo para: event store, claves-valor con acceso conocido por clave, o volúmenes con picos que exigen escalado sin gestión.
- **SHOULD** usar OpenSearch solo como read model de búsqueda/texto y Redis solo como caché o estructura efímera: ninguno es fuente de verdad.
- **MUST NOT** introducir un almacén "por moda" o por currículum del equipo.

## dynamodb-data-modeling

- **MUST** listar primero los patrones de acceso (consulta, frecuencia, consistencia, orden) y derivar de ellos claves e índices; no modelar entidades primero.
- **MUST** resolver cada patrón con `GetItem`/`Query`; **MUST NOT** usar `Scan` en rutas de negocio.
- **MUST** elegir una partition key de alta cardinalidad y reparto uniforme; **MUST NOT** usar claves de baja cardinalidad (`status`, fecha del día) como partition key.
- **SHOULD** usar prefijos tipados en las claves (`ORDER#123`, `CUSTOMER#9`) y un sort key que permita `begins_with` y rangos.
- **SHOULD** empezar con una tabla por bounded context (single-table por agregado relacionado solo si el equipo lo domina); no mezclar contextos en una tabla por "ahorrar".
- **MUST** tratar los GSI como eventualmente consistentes y como coste de escritura adicional; límite por defecto de 20 GSI por tabla (ver fuente).
- **MUST** paginar con `LastEvaluatedKey` y limitar el tamaño de respuesta; **MUST NOT** asumir joins ni agregaciones.
- **MUST** usar escrituras condicionales (`conditionExpression`) para unicidad y concurrencia optimista.
- **MUST** respetar el tamaño máximo de ítem (400 KB; comprobar en cuotas vigentes); los blobs van a S3 con referencia.

## dynamodb-event-store

- **MUST** modelar un stream por agregado: `pk = <TYPE>#<aggregateId>`, `sk` = versión con ceros a la izquierda (`v0000000042`) para ordenar lexicográficamente.
- **MUST** añadir con escritura condicional `attribute_not_exists(pk)` sobre la clave completa `(pk, sk)`: dos escritores con la misma versión esperada, uno falla (concurrencia optimista).
- **MUST** escribir varios eventos del mismo comando en un solo `TransactWriteItems` (misma tabla, misma región) y respetar sus límites (comprobar en la guía de la API).
- **MUST** publicar desde el propio almacén con DynamoDB Streams (o equivalente); **MUST NOT** publicar en el bus como segundo paso del comando (doble escritura).
- **MUST** tratar los consumidores como at-least-once: idempotentes por `(streamId, version)` (`idempotency-and-deduplication`).
- **MUST NOT** actualizar ni borrar ítems de eventos; la política IAM de la aplicación solo permite `PutItem` condicional y `Query`.
- **SHOULD** guardar metadatos: `type`, `schemaVersion`, `occurredAt`, `correlationId`, `causationId`, `payload`.
- **SHOULD** configurar retención y orden de Streams según la documentación vigente (comprobar retención de 24 h de los registros de Streams).
- **MUST** fijar la región de escritura por agregado si hay Global Tables (`global-tables-and-write-region-rules`).

## event-versioning-and-upcasting

- **MUST** guardar `type` y `schemaVersion` en cada evento.
- **MUST** preferir cambios compatibles: añadir campos opcionales con valor por defecto; no cambiar significado ni tipo de un campo existente.
- **MUST** para cambios incompatibles crear una versión nueva (`OrderPlacedV2`) y un upcaster `V1 -> V2` que se aplique al leer.
- **MUST** encadenar upcasters (`V1->V2->V3`); el dominio solo ve la última versión.
- **MUST** cubrir cada upcaster con un test usando un payload real de la versión antigua (fixture congelado).
- **MUST NOT** reescribir ni migrar masivamente los eventos almacenados para "limpiar" versiones (rompe inmutabilidad y auditoría); si un cambio de almacén lo exige, hacerlo como nueva copia verificable.
- **MUST NOT** borrar o renombrar un tipo de evento mientras existan streams que lo contienen.
- **SHOULD** registrar en el esquema (`schema-registry-and-evolution`) las versiones y su compatibilidad.
- **SHOULD** mantener upcasters puros y sin I/O; si falta un dato, usar un valor por defecto explícito y documentado.

## gdpr-and-immutable-events

- **MUST** clasificar los campos de cada tipo de evento (ver `pii-and-data-classification`) antes de definirlo; el payload mínimo es el que no necesita PII.
- **MUST** guardar los datos personales fuera del evento (tabla de perfil mutable) y referenciarlos por `subjectId` opaco, o cifrarlos con una clave por sujeto (crypto-shredding).
- **MUST** que borrar al sujeto sea destruir su clave o su fila de perfil; el evento sigue siendo válido y reproducible con el dato "olvidado".
- **MUST** que las proyecciones y copias derivadas (búsqueda, caché, data lake) también purguen al sujeto; documentar el mapa de copias.
- **MUST** custodiar las claves por sujeto en KMS/Vault OSS con copia de seguridad coherente: restaurar una copia antigua NO debe resucitar una clave destruida (registrar los borrados y reaplicarlos).
- **MUST NOT** reescribir ni borrar eventos del store para cumplir una supresión salvo decisión explícita con ADR; rompe hashes, versiones y proyecciones.
- **MUST NOT** poner PII en claves de stream, tipos de evento, cabeceras o logs.
- **SHOULD** definir plazos de retención por categoría y automatizar la destrucción de claves.

## global-tables-and-write-region-rules

- **MUST** elegir el modo de consistencia al crear la tabla; no se puede cambiar después: MREC (por defecto, asíncrono) o MRSC (síncrono, exactamente tres regiones).
- **MUST** con MREC asumir replicación asíncrona y conflictos "last writer wins" por ítem: la versión esperada del event store solo protege dentro de una región.
- **MUST** fijar UNA región de escritura por agregado (o por tenant) y documentarla; las demás réplicas solo leen o actúan como standby.
- **MUST** imponer la región de escritura con IAM/enrutado (política que deniega escritura en otras regiones, enrutado por tenant), no solo por convención.
- **MUST NOT** hacer escrituras concurrentes del mismo agregado en dos regiones con MREC.
- **MUST NOT** asumir atomicidad de `TransactWriteItems` entre regiones con MREC: solo es atómica en la región de origen.
- **SHOULD** evaluar MRSC solo si se exige RPO cero y lecturas fuertes multi-región; asumir mayor latencia de escritura y sus restricciones (sin transacciones, sin TTL, sin LSI).
- **MUST** definir el procedimiento de conmutación (failover) de la región de escritura de un agregado y probarlo en simulación antes de confiar en él.
- **MUST** probar conmutación y conflictos solo en pruebas y simulaciones; la fábrica no despliega (ADR-0004): preparado para AWS, no verificado en real.

## local-vs-aws-dynamodb-testing

- **MUST** probar contra DynamoDB Local (jar o imagen Docker oficial) en perfil `test`/`local`, con endpoint tomado de configuración y no fijo en código de producción.
- **MUST** declarar en el README del proyecto generado los límites del emulador y marcar el resultado como "preparado para AWS, no verificado en real".
- **MUST** tener en cuenta estas diferencias documentadas por AWS: throughput aprovisionado ignorado (no hay throttling), `Scan` paralelo no soportado (`Segment`/`TotalSegments` ignorados), lecturas casi siempre parecen fuertes, no se lanzan `TransactionConflictException`, límite de 1 MB en consultas sobre índices calculado distinto, nombres de tabla sin distinción de mayúsculas, sin PITR, sin tags, sin soporte de vector indexes.
- **MUST** simular con un doble (mock/stub del cliente) los errores que el emulador no genera: `TransactionConflictException`, `ProvisionedThroughputExceededException`, `ThrottlingException`; verificar reintentos y backoff.
- **MUST NOT** deducir capacidad, costes ni latencias de los tests locales.
- **MUST NOT** usar credenciales reales; usar literales `example`/`changeme` (el emulador exige clave y región, solo alfanuméricas en la clave).
- **SHOULD** crear tablas por código o script en `@BeforeAll`, con el mismo esquema/índices que el IaC (ver Terraform del proyecto) y una comprobación de que coinciden.
- **SHOULD** no depender de la forma de los shards de Streams: AWS indica que pueden diferir localmente.

## mongodb-alternative

- **MUST** descartar antes Postgres con `jsonb` e índices GIN, que cubre muchos casos documentales sin almacén nuevo.
- **MUST** abrir un ADR con la comparación, el coste operativo (`polyglot-operations-cost`) y el plan de salida.
- **MUST** revisar la licencia y el modelo de distribución antes de elegir edición o servicio gestionado; la fábrica evita licencias de pago por defecto (D16). Comprobar licencia vigente de MongoDB Community Server y términos de la edición elegida.
- **MUST** mantener las mismas reglas de oro: una fuente de verdad por agregado, sin doble escritura con Postgres, proyecciones derivadas.
- **MUST NOT** usarlo como event store sin demostrar equivalente de append condicional por versión (índice único `(streamId, version)`).
- **SHOULD** tratar Amazon DocumentDB como producto distinto con API compatible, no como MongoDB; comprobar qué funciones soporta (comprobar al fijar la versión).
- **SHOULD** preferir el emulador/contenedor local para pruebas y declarar qué no se reproduce de la variante gestionada.

## outbox-and-cdc

- **MUST** escribir el cambio de estado y la fila `outbox` en la misma transacción local; NUNCA estado en la BD y publicar al broker en el mismo método sin outbox (doble escritura).
- **MUST** que el relay (polling o CDC) entregue al-menos-una-vez; los consumidores MUST ser idempotentes usando el `id` del evento.
- **MUST** que cada fila outbox lleve `id`, `aggregate_type`, `aggregate_id`, `type`, `payload`, `created_at`; la clave del mensaje es `aggregate_id` para conservar orden por aggregate.
- **MUST** purgar o archivar filas procesadas (retención definida); el outbox es una cola, no un histórico.
- **SHOULD** preferir CDC (Debezium `EventRouter`) cuando el volumen o la latencia penalizan el polling; polling con `SELECT ... FOR UPDATE SKIP LOCKED` es suficiente para volúmenes bajos.
- **MUST NOT** asumir orden global entre aggregates; solo por clave.
- En DynamoDB: **MUST** escribir ítem de estado y de outbox con `TransactWriteItems` (hasta 100 acciones y 4 MB) y relevar con DynamoDB Streams, que retiene 24 h: el relay debe estar operativo dentro de esa ventana o se pierden eventos.
- **MUST NOT** asumir que los registros de Streams de una misma transacción llegan juntos ni en orden entre ítems; solo hay orden por ítem.

## polyglot-operations-cost

- **MUST** rellenar una ficha de coste por almacén extra antes de aprobar su uso (tabla del ejemplo).
- **MUST** incluir en la ficha: backup y restauración probados, migraciones/evolución de esquema, observabilidad, alertas, seguridad (cifrado, IAM), runbook y propietario.
- **MUST** incluir un informe de coste estimado sin desplegar (Infracost o equivalente sobre el plan, ver brief 4.6); es una estimación, no una medición.
- **MUST** definir cómo se reconstruye cada almacén derivado (OpenSearch, Redis) desde la fuente de verdad.
- **SHOULD** limitar el proyecto a un máximo de dos almacenes persistentes de verdad salvo ADR explícito.
- **SHOULD** reservar capacidad de formación del equipo en la ficha: modelado DynamoDB o relevancia en OpenSearch no se improvisan.
- **MUST NOT** aprobar un almacén sin dueño de guardia ni procedimiento de recuperación.

## projections-and-read-models

- **MUST** tratar la proyección como derivada y descartable: se puede borrar y reconstruir desde los eventos (`rebuilds-and-replays`).
- **MUST NOT** escribir la proyección desde el comando, ni permitir que otro proceso la modifique; solo el consumidor de eventos escribe.
- **MUST** hacer el consumidor idempotente: guardar el `(streamId, version)` aplicado y descartar duplicados o eventos anteriores.
- **MUST** persistir el checkpoint (última posición) en la misma transacción que el cambio de la proyección cuando el destino es Postgres.
- **MUST** asumir entrega at-least-once y orden garantizado solo dentro de un stream; no depender del orden entre streams.
- **MUST** exponer en la API que la vista es eventualmente consistente (por ejemplo `lastAppliedVersion`) y no leer de ella para decidir un comando.
- **MUST NOT** guardar en la proyección datos que no deriven de eventos.
- **SHOULD** una proyección por necesidad de consulta; evitar la vista "universal".
- **SHOULD** monitorizar el retraso (lag) y alertar por encima de un umbral acordado.
- **MUST** aplicar las mismas reglas de supresión de datos personales a las proyecciones (`gdpr-and-immutable-events`).

## rebuilds-and-replays

- **MUST** poder reconstruir cualquier proyección desde el log completo; si no se puede, no es una proyección sino una segunda fuente de verdad (prohibido por 4.5, sin doble escritura).
- **MUST** hacer el rebuild en una proyección nueva (versión N+1) y conmutar la lectura al terminar (blue/green); nunca vaciar la vista en uso.
- **MUST** guardar el checkpoint (último `global_position` aplicado) en la misma transacción que el efecto en la vista, para reanudar sin duplicar.
- **MUST** que los handlers de proyección sean idempotentes y deterministas: sin `Instant.now()`, sin llamadas a servicios externos, sin leer otras vistas.
- **MUST** que un replay no dispare efectos laterales (emails, publicación a Kafka, webhooks); separar proyectores de reacciones (`process managers`).
- **SHOULD** procesar en lotes y limitar el ritmo para no competir con el tráfico de lectura/escritura del almacén de eventos.
- **SHOULD** medir y documentar la duración del rebuild completo con volumen realista; es un runbook, no una sorpresa.
- **MUST NOT** depender de la retención de un broker (p. ej. 24 h en DynamoDB Streams) para reconstruir: la fuente es el event store.

## snapshots

- **MUST** medir antes: número de eventos por stream y tiempo de carga; documentar el umbral que justifica el snapshot.
- **MUST** tratar el snapshot como caché reconstruible, nunca como fuente de verdad: borrarlos todos no debe perder información.
- **MUST** guardar con el snapshot la `version` del último evento aplicado y un `snapshotSchemaVersion`.
- **MUST** cargar: último snapshot válido + eventos con `version` posterior; si el esquema del snapshot no coincide, ignorarlo y reconstruir desde los eventos.
- **MUST** escribir el snapshot de forma asíncrona o fuera de la ruta del comando, y tolerar que falle.
- **MUST NOT** actualizar el snapshot en la misma operación que decide el estado como si fuera un segundo estado (sería una segunda fuente de verdad).
- **SHOULD** crear snapshots cada N eventos (N medido, p. ej. múltiplo de 100: comprobar con datos del proyecto) o por tiempo.
- **SHOULD** guardarlos con clave separada del stream (`pk = SNAPSHOT#ORDER#<id>`) para no mezclarlos con eventos.
- **MUST** probar que `fold(eventos)` y `snapshot + eventos posteriores` dan el mismo estado.

## testing-event-sourced-systems

- **MUST** testear aggregates con el patrón given (eventos pasados) - when (comando) - then (eventos nuevos o excepción); sin mocks de repositorio ni base de datos.
- **MUST** que el aggregate sea puro: sin reloj ni UUID internos; inyectar `Clock` e identificadores desde el comando.
- **MUST** tener un test por cada upcaster con un evento histórico real guardado como fixture (JSON versionado en `src/test/resources`).
- **MUST** tener un test de concurrencia optimista: dos comandos con la misma versión esperada, uno debe fallar con conflicto.
- **MUST** tener un test de reconstrucción: proyección viva == proyección reconstruida desde cero (ver `rebuilds-and-replays`).
- **SHOULD** usar property-based testing para invariantes ("el saldo nunca es negativo para cualquier secuencia válida"; ver `property-based-testing`).
- **SHOULD** probar el event store contra el motor real (Testcontainers para Postgres; para DynamoDB ver `local-vs-aws-dynamodb-testing`).
- **MUST NOT** comparar eventos por `toString()` o timestamps reales; comparar records por igualdad con reloj fijo.

## when-to-use-and-when-not

- **MUST** responder por escrito a "¿los eventos SON el negocio?" (saldos, pólizas, expedientes, pedidos con historia): si no, no hay event sourcing.
- **MUST** distinguir tres necesidades y elegir la más barata que la cubra:
  1. Publicar hechos a otros sistemas: outbox (estado en Postgres + evento en la misma transacción).
  2. Saber quién cambió qué y cuándo: audit trail inmutable (`audit-trail-without-event-sourcing`).
  3. Reconstruir el estado en cualquier instante y derivar vistas de la historia: event sourcing.
- **MUST** recordar que event sourcing NO es auditoría: no la sustituye ni es la forma barata de obtenerla.
- **MUST NOT** combinar outbox y event sourcing en el mismo agregado: en event sourcing el almacén de eventos es la fuente de verdad y se publica desde él.
- **MUST NOT** hacer doble escritura del agregado en Postgres y en el event store.
- **MUST** abrir un ADR con alternativas descartadas, plan de versionado, de proyecciones y de supresión de datos personales (`gdpr-and-immutable-events`).
- **SHOULD** aplicarlo solo a agregados concretos, no a todo el sistema.
