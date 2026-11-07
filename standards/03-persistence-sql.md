# Estándares · 03-persistence-sql

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## auditing-soft-delete-history

- **MUST** auditar con mecanismo central (`@EntityListeners(AuditingEntityListener.class)` + `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy`), no a mano en cada servicio.
- **MUST** guardar instantes en UTC (`Instant`, `timestamptz`) y el autor como identificador estable del sujeto (claim `sub`), no nombre visible.
- **MUST** decidir por entidad entre borrado físico, lógico o archivado; el borrado lógico no es el defecto.
- **MUST** con borrado lógico: filtrar en todas las lecturas (`@SQLRestriction` de Hibernate, TODO-VERIFY nombre según versión), excluir filas borradas de índices únicos con índice parcial (`WHERE deleted_at IS NULL`) y definir una purga con plazo.
- **MUST** tratar el derecho de supresión: un borrado lógico NO cumple una petición de supresión de datos personales (ver `data-privacy-in-db`).
- **MUST NOT** usar historial como sustituto de backup ni como bus de eventos.
- **SHOULD** para historial completo preferir Hibernate Envers o tablas `_history` mediante trigger; elegir una y documentarla. Envers duplica escrituras y crece: definir retención.
- **SHOULD** que el historial sea append-only y que la aplicación no tenga permisos de UPDATE/DELETE sobre él.

## batching-and-bulk-ops

- **MUST** activar batching de JDBC explícitamente: `spring.jpa.properties.hibernate.jdbc.batch_size` (p. ej. 50) junto con `order_inserts=true` y `order_updates=true`.
- **MUST** recordar que `GenerationType.IDENTITY` desactiva el batching de inserts en Hibernate; usar `SEQUENCE` con `allocationSize` coherente (ver `id-generation`).
- **MUST** procesar cargas grandes en trozos (chunks) con una transacción por trozo y `flush()` + `clear()` del `EntityManager` al final de cada uno.
- **MUST** usar `@Modifying` JPQL/SQL (bulk) para actualizaciones/borrados masivos uniformes, sabiendo que saltan el contexto de persistencia: `clearAutomatically = true`.
- **MUST NOT** hacer `deleteAll()` o `findAll()` + bucle para borrar/actualizar miles de filas.
- **MUST NOT** cargar todo el resultado en memoria; usar paginación por clave (keyset) o `Stream` dentro de transacción de solo lectura.
- **SHOULD** usar `JdbcTemplate.batchUpdate` o jOOQ batch cuando no se necesite el modelo de entidades (ver `jdbc-and-jooq`).
- **SHOULD** hacer los procesos reanudables e idempotentes (marca de progreso por chunk).
- **SHOULD** medir con el conteo de sentencias/batches, no a ojo.

## caching

- **MUST** medir antes de cachear: identificar la consulta lenta o frecuente y corregir antes N+1, índices y proyecciones (ver `n-plus-one`, `indexing-and-query-plans`).
- **MUST** definir por caché: clave, TTL, tamaño máximo y estrategia de invalidación; sin TTL ni límite no se despliega.
- **MUST** incluir el tenant (y cualquier dimensión de autorización) en la clave en sistemas multi-tenant (ver `multi-tenancy`).
- **MUST NOT** cachear entidades JPA gestionadas en una caché de aplicación; cachear DTOs/valores inmutables.
- **MUST NOT** cachear datos sensibles o PII sin decisión explícita (ver `data-privacy-in-db`).
- **MUST NOT** cachear dentro de una transacción esperando consistencia fuerte: la caché puede servir un valor anterior al commit.
- **SHOULD** limitar la caché de 2º nivel de Hibernate a entidades de lectura casi exclusiva (catálogos, configuración).
- **SHOULD** exponer métricas de hit ratio y evicciones (Micrometer) y alertar sobre ratios bajos.
- **SHOULD** proteger contra stampede (carga única por clave: `sync = true` en `@Cacheable`).

## connection-pooling

- **MUST** usar HikariCP (defecto de Spring Boot) con `maximum-pool-size` explícito; no heredar el defecto sin pensarlo.
- **MUST** dimensionar pequeño: el total de conexiones es `instancias x maximum-pool-size` y debe caber en `max_connections` de la BD con margen para mantenimiento y otros servicios.
- **MUST** fijar `connection-timeout` (fallar rápido, no esperar el defecto) y `max-lifetime` menor que cualquier timeout de red/proxy/BD intermedio.
- **MUST NOT** mantener una conexión mientras se hace I/O lento externo (HTTP, colas) dentro de una transacción (ver `transactions`).
- **MUST NOT** subir el pool como respuesta a "pool agotado" sin buscar antes transacciones largas o fugas.
- **SHOULD** activar `leak-detection-threshold` en entornos no productivos para detectar fugas.
- **SHOULD** exponer métricas del pool (`hikaricp.connections.*` vía Micrometer) y alertar sobre `pending` > 0 sostenido.
- **SHOULD** considerar un pooler externo (PgBouncer) cuando haya muchas instancias; revisar compatibilidad con prepared statements y modo de transacción.
- **SHOULD** usar pools separados para cargas distintas (online vs. batch) para que una no deje sin conexiones a la otra.

## data-privacy-in-db

- **MUST** clasificar cada columna personal (público/interno/PII/sensible) en el diseño; documentar propósito y plazo de retención por columna o tabla.
- **MUST** minimizar: no almacenar lo que no se necesita; no copiar PII a tablas de informes, logs ni cachés sin necesidad.
- **MUST** cifrar en tránsito (TLS hacia la BD) y en reposo (cifrado de disco/volumen del proveedor); para campos especialmente sensibles, cifrado a nivel de aplicación con claves fuera de la BD (ver `secrets-management`, `crypto-tls-mtls-key-rotation`).
- **MUST NOT** guardar contraseñas ni secretos en claro; usar hash adaptativo (ver `authn-oidc-oauth2`) y delegar la identidad al IdP (Keycloak) cuando sea posible.
- **MUST NOT** copiar datos de producción a desarrollo/test; usar datos sintéticos o anonimizados de forma irreversible.
- **MUST** poder cumplir una petición de supresión/acceso: localizar todos los datos de un sujeto y borrarlos o anonimizarlos, incluidas copias, historial y archivos (ver `auditing-soft-delete-history`, `partitioning-and-archival`).
- **MUST** limitar el acceso: roles de BD de mínimo privilegio, sin cuentas de aplicación con DDL; vistas o columnas restringidas para soporte/analítica.
- **SHOULD** enmascarar PII en logs, trazas y mensajes de error; no incluirla en claves de caché ni en URLs.
- **SHOULD** pseudonimizar (id interno) en datos analíticos y separar la tabla de identidad de los datos de actividad.
- **SHOULD** registrar accesos a datos sensibles (ver `audit-trail-and-security-logging`).

## db-design-conventions

- **MUST** nombres en inglés, `snake_case`, tablas en singular o plural según una única convención del proyecto, sin palabras reservadas ni comillas obligatorias.
- **MUST** clave primaria en toda tabla; estrategia de ids según `id-generation`.
- **MUST** declarar `NOT NULL` por defecto; `NULL` solo si "desconocido" es un estado de negocio real.
- **MUST** integridad en la BD, no solo en la aplicación: `FOREIGN KEY`, `UNIQUE`, `CHECK` (estados válidos, importes >= 0).
- **MUST** dinero como `numeric(p,s)` (o enteros en la unidad menor) más moneda (código ISO 4217); nunca `float`/`double`.
- **MUST** instantes como `timestamptz` en UTC; fechas de calendario como `date`; nunca guardar fechas como texto.
- **MUST** nombrar explícitamente constraints e índices (`pk_`, `fk_`, `uq_`, `chk_`, `idx_`) para que las migraciones sean predecibles.
- **MUST NOT** usar `text` libre para valores de dominio cerrado sin `CHECK` o tabla de referencia; evitar enums nativos de BD si cambian a menudo (añadir valores es migración).
- **MUST NOT** guardar listas separadas por comas ni JSON para datos que se consultan o relacionan; `jsonb` solo para atributos realmente flexibles, indexado si se filtra.
- **SHOULD** columnas de auditoría coherentes (ver `auditing-soft-delete-history`) y tamaños acotados (`varchar(n)` o `CHECK (length(...))`) donde el dominio los tenga.
- **SHOULD** desnormalizar solo con medición que lo justifique y documentándolo.

## db-testing

- **MUST** probar contra el mismo motor y versión mayor que producción (PostgreSQL con Testcontainers); **MUST NOT** usar H2 "en modo PostgreSQL" para validar SQL, locking, JSON o RLS.
- **MUST** crear el esquema con las migraciones reales (Flyway) en los tests de persistencia, no con `ddl-auto=create` (ver `schema-migrations`).
- **MUST** reutilizar el contenedor entre tests de la suite (singleton / `@ServiceConnection`, TODO-VERIFY versión de Spring Boot) para tiempos razonables.
- **MUST** aislar los tests: datos únicos por test o limpieza explícita; no depender del orden. Tener en cuenta que `@Transactional` + rollback no prueba el commit real ni el locking entre transacciones.
- **MUST** tener tests de concurrencia reales (dos transacciones, hilos) para `optimistic-locking` y `pessimistic-locking`, y tests de conteo de sentencias en consultas críticas (ver `n-plus-one`).
- **MUST** incluir en tests los casos de aislamiento multi-tenant y RLS cuando aplique (ver `multi-tenancy`).
- **SHOULD** usar `@DataJpaTest` con `@AutoConfigureTestDatabase(replace = NONE)` para slices de persistencia.
- **SHOULD** usar builders de datos de prueba, no volcados SQL opacos; nunca datos reales de producción ni PII (ver `test-data-management`).
- **SHOULD** ejecutar `flush()` + `clear()` antes de verificar para forzar lectura real desde la BD.

## id-generation

- **MUST** decidir la estrategia por entidad y documentarla si se desvía del defecto del proyecto.
- **SHOULD** usar `SEQUENCE` con `allocationSize` igual al `INCREMENT BY` de la secuencia en BD, para permitir batching de inserts (ver `batching-and-bulk-ops`).
- **MUST NOT** usar `GenerationType.AUTO` sin saber qué estrategia resuelve el dialecto.
- **MUST NOT** asumir que `IDENTITY` permite batch de inserts: Hibernate debe insertar para conocer el id.
- **SHOULD** usar UUID (preferible v7, ordenable por tiempo) cuando el id se genera fuera de la BD o en sistemas distribuidos; guardarlo con tipo `uuid` nativo, no `varchar(36)`.
- **MUST NOT** usar UUID v4 aleatorio como PK en motores que ordenan físicamente por PK sin medir el impacto en índices.
- **MUST NOT** exponer ids secuenciales enumerables en APIs públicas cuando la enumeración sea un riesgo; usar un id público separado.
- **MUST NOT** generar ids con `max(id)+1`.

## indexing-and-query-plans

- **MUST** indexar las columnas de claves foráneas usadas en joins/borrados (PostgreSQL no las indexa automáticamente).
- **MUST** diseñar índices desde las consultas reales: orden de columnas compuestas = igualdad primero, luego rango/orden.
- **MUST** revisar con `EXPLAIN (ANALYZE, BUFFERS)` sobre un volumen de datos realista las consultas críticas antes de aprobar; un Seq Scan sobre tabla grande necesita justificación.
- **MUST** respaldar cada índice con una consulta que lo use; los índices cuestan escrituras y espacio. Eliminar los no usados (`pg_stat_user_indexes`) tras observar un ciclo completo de carga.
- **MUST NOT** envolver la columna indexada en funciones (`lower(email) = ...`) sin un índice de expresión equivalente.
- **MUST NOT** fiarse del plan en una BD de desarrollo con 100 filas.
- **SHOULD** usar índices parciales (`WHERE deleted_at IS NULL`), de cobertura (`INCLUDE`) y GIN/BRIN donde encajen, justificándolo con un plan.
- **SHOULD** mantener estadísticas al día (autovacuum) y vigilar `pg_stat_statements` para detectar las consultas más costosas (TODO-VERIFY extensión disponible en el entorno).
- **SHOULD** crear índices con `CONCURRENTLY` (ver `schema-migrations`).

## isolation-levels-and-anomalies

- **MUST** conocer el nivel por defecto del motor de producción (PostgreSQL: READ COMMITTED; MySQL/InnoDB: REPEATABLE READ) y no asumir que es igual en todos — TODO-VERIFY contra la documentación del motor y versión elegidos.
- **MUST** identificar las anomalías posibles de cada caso de uso: lost update, non-repeatable read, phantom, write skew.
- **MUST** proteger el patrón "leer y luego escribir según lo leído" con bloqueo (`optimistic-locking`/`pessimistic-locking`), una restricción de BD o un `UPDATE` atómico condicional; no confiar en el aislamiento por defecto.
- **SHOULD** preferir restricciones declarativas (`UNIQUE`, `CHECK`, FK) como última defensa de invariantes.
- **SHOULD** usar `UPDATE ... SET stock = stock - :n WHERE id = :id AND stock >= :n` en lugar de leer, restar y guardar.
- **MUST** reintentar las transacciones abortadas por fallos de serialización o deadlock (SQLSTATE `40001`/`40P01` en PostgreSQL) si se usa `SERIALIZABLE` o bloqueos.
- **MUST NOT** subir globalmente a `SERIALIZABLE` como "solución"; hacerlo solo por caso de uso, con reintentos y medición.
- **MUST** documentar el nivel elegido junto al `@Transactional(isolation = ...)`.

## jdbc-and-jooq

- **MUST** parametrizar siempre: `?`/parámetros nombrados o los bind values de jOOQ; nunca concatenar entrada en el SQL (ver `sql-injection-prevention`).
- **MUST** documentar la elección en `query-strategy`: JPA para escritura de agregados, SQL explícito para lecturas complejas (CQS pragmático).
- **MUST** mantener una sola vía de escritura por agregado; no mezclar JPA y SQL directo sobre la misma tabla dentro de una transacción sin hacer `flush()` antes y `clear()` después.
- **MUST** que JDBC/jOOQ usen el mismo `DataSource` y transacción de Spring (`DataSourceTransactionManager`/`JpaTransactionManager` con el mismo `DataSource`) para participar de `@Transactional`.
- **MUST NOT** devolver `ResultSet` ni tipos de jOOQ (`Record`) fuera de la capa de persistencia; mapear a DTOs/records.
- **SHOULD** preferir `JdbcClient`/`NamedParameterJdbcTemplate` sobre `JdbcTemplate` con `Object[]` posicional (TODO-VERIFY disponibilidad de `JdbcClient` según versión de Spring).
- **SHOULD** con jOOQ, generar el código desde el esquema real de las migraciones (en build) para que el compilador detecte cambios de esquema. Usar la edición OSS (D16): confirmar que el dialecto necesario está en la edición Open Source (TODO-VERIFY licencia).
- **SHOULD** usar `batchUpdate` para escrituras masivas (ver `batching-and-bulk-ops`).

## joins-and-fetch-joins

- **MUST** distinguir `JOIN` (filtra/une, no inicializa) de `JOIN FETCH` (inicializa la asociación en la entidad).
- **MUST NOT** hacer `JOIN FETCH` de más de una colección (`List`) en la misma consulta: producto cartesiano y `MultipleBagFetchException`. Cargar la segunda con otra consulta o `@BatchSize`.
- **MUST NOT** combinar `JOIN FETCH` de colección con `Pageable`/`setMaxResults`: Hibernate pagina en memoria (aviso `HHH000104`). Paginar ids primero y luego cargar con fetch.
- **MUST** usar `DISTINCT` (o `Set`) solo cuando el fetch de colección duplica la raíz; comprobar si la versión de Hibernate ya deduplica (TODO-VERIFY).
- **SHOULD** usar `LEFT JOIN FETCH` si la asociación puede faltar; `JOIN FETCH` interno descarta filas sin relación.
- **SHOULD** preferir `@EntityGraph` en repositorios Spring Data para casos simples y `JOIN FETCH` explícito para los complejos.
- **MUST NOT** filtrar sobre un alias de `JOIN FETCH` de colección: la colección cargada queda incompleta.

## jpa-entity-design

- **MUST NOT** usar Lombok (`@Data`, `@Getter`, etc.; D27): escribir getters y constructores a mano.
- **MUST** tener un constructor sin argumentos `protected` (exigido por JPA) y un constructor público o factoría que deje la entidad en estado válido.
- **MUST** mapear enums con `@Enumerated(EnumType.STRING)`; nunca `ORDINAL`.
- **MUST** basar `equals`/`hashCode` en el id o en una clave de negocio inmutable; nunca en todos los campos ni en colecciones perezosas.
- **MUST NOT** usar entidades como DTO de API: el contrato HTTP no debe acoplarse al esquema.
- **MUST** mantener coherentes los dos lados de una relación bidireccional con métodos de ayuda (`addLine`) y `mappedBy` en el lado inverso.
- **SHOULD** usar tipos de valor (`@Embeddable`) para conceptos como `Money` o `Address`.
- **SHOULD** declarar `@Column(nullable = false, length = ...)` coherente con el DDL de la migración.
- **MUST NOT** usar `CascadeType.REMOVE`/`ALL` sobre asociaciones hacia otros agregados.

## lazy-vs-eager

- **MUST** declarar `fetch = FetchType.LAZY` en toda asociación; el mapeo es perezoso y la carga se decide por caso de uso.
- **MUST NOT** usar `FetchType.EAGER` en el mapeo; si un caso de uso necesita datos relacionados, usar `JOIN FETCH`, `@EntityGraph` o DTO.
- **MUST NOT** resolver `LazyInitializationException` con `EAGER`, con `open-in-view` ni alargando transacciones.
- **MUST** mantener `spring.jpa.open-in-view=false`.
- **MUST** devolver desde la capa de servicio datos ya cargados (DTO o entidad inicializada), no proxies sin inicializar.
- **SHOULD** modelar `@OneToOne` desde el lado propietario o con `@MapsId`; el lado inverso no puede ser perezoso de forma fiable.
- **SHOULD** usar `Hibernate.initialize` solo dentro de la transacción y de forma excepcional.

## multi-tenancy

- **MUST** elegir y documentar (ADR) el modelo: discriminador en columna, schema por tenant o BD por tenant. Criterio: aislamiento exigido, nº de tenants, coste operativo, migraciones.
- **MUST** resolver el tenant una sola vez en el borde (token/claim validado), propagarlo por un contexto explícito y NO aceptarlo de parámetros del cliente.
- **MUST** con discriminador: columna `tenant_id NOT NULL` en cada tabla de negocio, incluida en índices únicos y claves foráneas compuestas; aplicar el filtro de forma centralizada (`@TenantId` de Hibernate 6.x, TODO-VERIFY versión mínima) y no query a query.
- **MUST** añadir Row Level Security de PostgreSQL como segunda barrera cuando el modelo sea por discriminador: política `USING (tenant_id = current_setting('app.tenant_id')::uuid)` y rol de aplicación sin `BYPASSRLS` ni ownership de las tablas.
- **MUST** fijar `app.tenant_id` con `SET LOCAL` dentro de la transacción (no `SET` de sesión) para que no se filtre al reutilizar la conexión del pool.
- **MUST** escribir tests de fuga entre tenants: datos del tenant A invisibles e inmodificables desde B, incluyendo queries nativas, jobs asíncronos y caché.
- **MUST NOT** ejecutar SQL nativo o jobs sin contexto de tenant; fallar cerrado si falta.
- **SHOULD** incluir el tenant en claves de caché y en logs/trazas (ver `caching`).
- **SHOULD** en schema/BD por tenant: pool por tenant acotado o pooler externo, y migraciones orquestadas con informe por tenant (ver `schema-migrations`).

## n-plus-one

- **MUST** definir todas las asociaciones `@ManyToOne`/`@OneToOne` como `FetchType.LAZY` (el defecto EAGER es una causa habitual de N+1).
- **MUST** cargar lo necesario por caso de uso: `JOIN FETCH`, `@EntityGraph` o proyección a DTO.
- **MUST NOT** acceder a asociaciones perezosas dentro de bucles sin haberlas cargado.
- **MUST NOT** hacer `JOIN FETCH` de dos colecciones a la vez (producto cartesiano / `MultipleBagFetchException`); usar consultas separadas o `@BatchSize`.
- **SHOULD** preferir proyecciones DTO para lecturas de listados.
- **SHOULD** usar `hibernate.default_batch_fetch_size` como red de seguridad, no como sustituto del diseño.
- **MUST** cubrir las consultas críticas con un test que cuente sentencias SQL.
- **MUST NOT** activar `open-in-view` (`spring.jpa.open-in-view=false`).

## optimistic-locking

- **MUST** añadir un atributo `@Version` (`long`/`Integer`/`Instant`; preferible numérico) a las entidades de agregado mutables compartidas.
- **MUST NOT** modificar el campo `@Version` a mano.
- **MUST** convertir `ObjectOptimisticLockingFailureException` (Spring) en una respuesta de conflicto (HTTP 409 Problem Details) o en reintento controlado.
- **MUST** reintentar solo operaciones idempotentes y con un tope de intentos (p. ej. 3) y espera con jitter; el reintento debe relanzar la transacción completa.
- **SHOULD** exponer la versión (ETag/`If-Match`) en APIs de edición para detectar conflictos entre peticiones HTTP separadas.
- **MUST NOT** capturar la excepción dentro de la misma transacción: el contexto queda inconsistente.
- **MUST** verificar que las actualizaciones masivas JPQL/SQL (`@Modifying`) incrementan la versión explícitamente (`update ... set version = version + 1`) o usar `versioned`; no lo hacen solas.
- **SHOULD** añadir la columna `version` en la migración con `NOT NULL DEFAULT 0`.

## pagination

- **MUST** limitar toda consulta de listado; ningún endpoint devuelve "todo" sin tope máximo de tamaño de página.
- **MUST** definir un orden total y determinista (`ORDER BY created_at, id`): sin desempate, las páginas duplican u omiten filas.
- **SHOULD** usar paginación por keyset (`where (created_at, id) > (:ts, :id)`) en tablas grandes o scroll infinito; `OFFSET` degrada linealmente con la profundidad.
- **SHOULD** devolver `Slice` (sin `count(*)`) cuando la UI no necesita el total.
- **MUST** dar a `Page` un `countQuery` propio si la consulta tiene joins o fetch (ver `joins-and-fetch-joins`).
- **MUST NOT** combinar `JOIN FETCH` de colección con paginación (se pagina en memoria).
- **MUST** respaldar el orden de paginación con un índice (ver `indexing-and-query-plans`).
- **MUST NOT** aceptar `size` sin validar (`@Max`) ni `sort` sin lista blanca.

## partitioning-and-archival

- **MUST** justificar el particionado con un problema medido (purga costosa, mantenimiento, consultas siempre acotadas por rango) y registrarlo en un ADR.
- **MUST** elegir una clave de partición que aparezca en las consultas habituales (normalmente fecha) para que haya poda de particiones; verificarlo con `EXPLAIN`.
- **MUST** tener en cuenta que la clave primaria y los índices únicos de una tabla particionada deben incluir la clave de partición (TODO-VERIFY en documentación de PostgreSQL de la versión usada).
- **MUST** automatizar la creación de particiones futuras y la retirada de antiguas; una partición que falta rompe las inserciones.
- **MUST** definir retención por tipo de dato (negocio, legal, PII) con base en requisitos confirmados; plazos legales son borrador por confirmar con fuente oficial.
- **MUST NOT** purgar con `DELETE` masivo cuando la partición permite `DETACH`/`DROP`.
- **SHOULD** archivar antes de borrar (exportar a almacenamiento barato, formato abierto) cuando haya obligación de conservar; verificar que el archivo se puede restaurar y leer.
- **SHOULD** que las migraciones de particionado se hagan con expand/contract y copia por lotes (ver `schema-migrations`, `batching-and-bulk-ops`).
- **SHOULD** respetar supresión de datos personales también en los archivos (ver `data-privacy-in-db`).

## persistence-context-and-flush

- **MUST** entender que dentro de una transacción las entidades gestionadas se sincronizan solas (dirty checking) al hacer flush; no hace falta `save()` tras modificar una entidad gestionada.
- **MUST NOT** esperar que los cambios estén en BD antes del commit: el flush ocurre en commit, antes de ciertas consultas (modo AUTO) o con `flush()` explícito.
- **SHOULD** llamar a `flush()` solo cuando se necesite detectar una violación de constraint en un punto concreto o antes de una consulta nativa sobre datos recién cambiados.
- **MUST** liberar el contexto (`flush()` + `clear()`) cada lote en procesos con miles de entidades para evitar crecimiento de memoria y dirty checking lento (ver `batching-and-bulk-ops`).
- **MUST NOT** guardar `EntityManager` ni entidades gestionadas en campos de singletons ni compartirlos entre hilos.
- **MUST** recordar que `@Modifying` en JPQL/SQL no actualiza las entidades ya cargadas: usar `clearAutomatically = true` o recargar.
- **SHOULD** marcar `@Transactional(readOnly = true)` en lecturas: evita snapshots para dirty checking en Hibernate (TODO-VERIFY detalle por versión).
- **MUST NOT** hacer `save()` en bucle sobre entidades ya gestionadas esperando un INSERT/UPDATE inmediato.
- **SHOULD** usar `getReferenceById` para asociar sin cargar la fila completa.

## pessimistic-locking

- **MUST** justificar por escrito por qué no basta bloqueo optimista o un `UPDATE` atómico.
- **MUST** definir siempre timeout de bloqueo (`jakarta.persistence.lock.timeout`, o `NOWAIT`/`lock_timeout` del motor) — TODO-VERIFY soporte por dialecto; nunca esperar indefinidamente.
- **MUST** mantener la transacción mínima: tomar el bloqueo tarde y soltarlo pronto (commit); sin I/O externo mientras se retiene.
- **MUST** adquirir bloqueos sobre varias filas/tablas siempre en el mismo orden (por id ascendente) para evitar deadlocks.
- **SHOULD** usar `FOR UPDATE SKIP LOCKED` para que varios workers reclamen filas de una tabla-cola sin pisarse.
- **MUST** manejar `PessimisticLockException`/`CannotAcquireLockException` y deadlocks con reintento acotado.
- **MUST NOT** usar `PESSIMISTIC_WRITE` en consultas con joins amplios; bloquea más filas de las previstas.
- **MUST NOT** sustituir con bloqueo de BD un lock distribuido entre servicios (ver `distributed-locking`).

## projections-and-dtos

- **MUST** usar proyección (record/interfaz/constructor expression) para lecturas que no modifican datos.
- **MUST NOT** cargar entidades completas para devolver 3 columnas.
- **SHOULD** usar `record` como DTO de proyección con constructor expression en JPQL: `select new ...`.
- **SHOULD** preferir proyecciones de clase (records) a proyecciones de interfaz dinámicas cuando el rendimiento importe; las de interfaz anidadas pueden cargar la entidad completa (TODO-VERIFY según versión de Spring Data).
- **MUST NOT** devolver entidades JPA desde controladores.
- **MUST** nombrar el DTO por caso de uso (`OrderSummary`), no por tabla.
- **SHOULD** usar proyecciones también para evitar N+1 en listados con datos de varias tablas.
- **MUST NOT** reutilizar un único DTO "gordo" para todos los casos de uso.

## query-strategy

- **MUST** elegir la herramienta más simple que cubra el caso: `findById`/derived query (1-2 criterios) → `@Query` JPQL (joins, proyecciones) → `Specification`/Criteria (filtros opcionales dinámicos) → SQL nativo o jOOQ (funciones del motor, CTE, ventanas, informes).
- **MUST NOT** usar derived queries con nombres de más de ~3 criterios (`findByStatusAndCustomerIdAndCreatedAtBetweenAndTotalGreaterThan...`): pasar a `@Query`.
- **MUST** parametrizar siempre (ver `sql-injection-prevention`).
- **SHOULD** centralizar filtros dinámicos en `Specification`s composables y testeadas, no en `if` que concatenan JPQL.
- **SHOULD** usar SQL nativo/jOOQ en informes complejos con DTO plano, aislado en un repositorio de lectura.
- **MUST** revisar el plan de ejecución de consultas nuevas sobre tablas grandes (ver `indexing-and-query-plans`).
- **MUST NOT** filtrar o ordenar en memoria (`stream().filter`) lo que la BD puede resolver.
- **MUST NOT** mezclar lecturas con 5+ joins en el repositorio del agregado; crear un repositorio de consulta.

## read-replicas-and-routing

- **MUST** enrutar solo por intención declarada: `@Transactional(readOnly = true)` hacia réplica, el resto al primario. Implementación típica: `AbstractRoutingDataSource` + `LazyConnectionDataSourceProxy` para decidir tras conocer el flag `readOnly`.
- **MUST** asumir retraso de replicación: una lectura en réplica puede no ver una escritura recién confirmada.
- **MUST** que los flujos "escribo y leo lo escrito" (read-your-writes), validaciones y lecturas dentro de transacciones de escritura vayan al primario.
- **MUST NOT** escribir ni bloquear (`FOR UPDATE`) contra una réplica; fallar de forma explícita.
- **MUST NOT** usar réplicas para decisiones que exijan consistencia fuerte (saldos, stock, unicidad).
- **SHOULD** tener pools y métricas separados por destino (ver `connection-pooling`) y health check que degrade a primario si la réplica cae o su retraso supera un umbral.
- **SHOULD** limitar el retraso aceptado por caso de uso y documentarlo.
- **SHOULD** tener en la matriz local una réplica de PostgreSQL solo si el equipo necesita probar el enrutado; el retraso real, failover y endpoints gestionados NO se reproducen en local. Preparado para AWS, no verificado en real.

## schema-migrations

- **MUST** gestionar el esquema solo con migraciones versionadas Flyway (`V<n>__descripcion.sql`) en el repo; `spring.jpa.hibernate.ddl-auto` en `none` o `validate`, nunca `update`/`create` fuera de tests efímeros.
- **MUST NOT** editar una migración ya aplicada en cualquier entorno compartido; corregir con una nueva versión (Flyway valida checksums).
- **MUST** aplicar expand/contract para cambios incompatibles: (1) expandir con columna/tabla nueva nullable, (2) desplegar código que escribe en ambos y lee de la nueva, (3) rellenar datos por lotes, (4) contraer en un release posterior.
- **MUST** que cada versión de la aplicación funcione con el esquema anterior y el siguiente (rolling deploy): no renombrar ni borrar columnas en el mismo release que deja de usarlas.
- **MUST** evitar bloqueos largos: `CREATE INDEX CONCURRENTLY` en PostgreSQL (fuera de transacción), añadir `NOT NULL`/FK en dos pasos (`NOT VALID` + `VALIDATE`), `lock_timeout` en la migración.
- **MUST NOT** mezclar DDL pesado y backfill masivo en una sola migración; el backfill va por lotes y reanudable.
- **SHOULD** una migración por cambio lógico, idempotente en su intención y revisada junto al código.
- **SHOULD** probar migraciones contra PostgreSQL real (Testcontainers) desde un esquema vacío y desde una copia de la versión anterior.
- **SHOULD** no depender de migraciones "undo" (de pago en Flyway Teams); el plan de vuelta atrás es avanzar con otra migración.

## sql-injection-prevention

- **MUST** pasar todo valor externo como parámetro enlazado (`:name`, `?`), nunca por concatenación ni `String.format`.
- **MUST NOT** construir identificadores (columna, tabla, `ORDER BY`) con entrada de usuario; mapearlos desde una lista blanca (`enum` o `Map`).
- **MUST** validar `Sort` de Spring Data contra propiedades permitidas antes de aplicarlo en consultas nativas o `@Query` con `#{#sort}`.
- **MUST** escapar los comodines de `LIKE` del usuario (`%`, `_`) cuando se busque literal.
- **SHOULD** usar `Specification`/Criteria o jOOQ con DSL tipado para filtros dinámicos.
- **MUST NOT** construir `IN (...)` concatenando; usar parámetro de colección.
- **MUST** conectar con un usuario de BD de mínimos privilegios (sin DDL en runtime).
- **MUST NOT** devolver mensajes de error SQL al cliente (ver `error-handling-problem-details`).

## transactions

- **MUST** colocar `@Transactional` en la capa de servicio/caso de uso, no en controladores ni repositorios.
- **MUST** marcar `readOnly = true` en los casos de uso de solo lectura.
- **MUST NOT** llamar a HTTP, colas o ficheros dentro de una transacción abierta: mantiene conexión y bloqueos durante la latencia externa. Usar outbox o ejecutar tras el commit (`@TransactionalEventListener(phase = AFTER_COMMIT)`).
- **MUST NOT** invocar un método `@Transactional` desde la misma clase (self-invocation): el proxy no interviene. Extraer a otro bean.
- **MUST** recordar que por defecto solo hace rollback con `RuntimeException`/`Error`; las excepciones comprobadas requieren `rollbackFor`.
- **MUST NOT** capturar y tragarse una excepción dentro de la transacción esperando que continúe; puede quedar marcada como solo-rollback.
- **SHOULD** mantener transacciones cortas, con el menor número de filas y bloqueos posible.
- **MUST** usar `REQUIRES_NEW` solo con justificación escrita (auditoría, outbox de errores) y consciente del segundo uso de conexión.
- **MUST NOT** usar `@Transactional` en métodos `private` o `final` esperando efecto.
