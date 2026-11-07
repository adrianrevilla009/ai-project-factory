# Estándares · 23-data-platform

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## access-control-masking-and-retention

- **MUST** conceder acceso a roles (grupos del IdP), nunca a usuarios individuales; mínimo privilegio por zona.
- **MUST** restringir raw a la plataforma de datos; analistas leen solo silver/gold.
- **MUST** enmascarar o seudonimizar columnas `restricted`/`pii` por defecto en gold; el dato claro requiere rol explícito y registro de acceso.
- **MUST** definir retención por dataset (`retention_days`) y automatizar su aplicación (TTL, particiones, ciclo de vida).
- **MUST NOT** copiar datos clasificados a hojas de cálculo, buckets personales o entornos de desarrollo.
- **MUST NOT** usar datos de producción sin enmascarar en entornos no productivos.
- **SHOULD** aplicar seguridad por fila (row filter) para datos multi-tenant o regionales.
- **SHOULD** usar hash con sal gestionada (HMAC) para claves seudonimizadas que deban poder unirse entre tablas.

## batch-orchestration

- **MUST** hacer cada tarea idempotente y parametrizada por intervalo de datos (no por `now()`): re-ejecutar el mismo intervalo da el mismo resultado.
- **MUST** escribir con patrón "overwrite de partición" o `MERGE`, nunca `INSERT` ciego.
- **MUST** fijar `catchup=False` por defecto; los backfills son una acción explícita y acotada.
- **MUST** definir reintentos con backoff y timeout por tarea, y alerta ante fallo final.
- **MUST** leer credenciales de un backend de secretos (Vault OSS, D16), no de variables de DAG ni del código.
- **MUST NOT** hacer trabajo pesado en el scheduler/parseo del DAG (consultas o llamadas de red a nivel de módulo).
- **MUST NOT** pasar datasets grandes por XCom/metadatos; pasar referencias (ruta, partición).
- **SHOULD** preferir modelo por activos (Dagster) o datasets/assets (Airflow) cuando el dato es el objeto de gestión; DAG de tareas si es proceso.
- **SHOULD** emitir eventos OpenLineage (ver `data-contracts-and-lineage`).
- **SHOULD** separar orquestación de transformación: el orquestador llama a dbt/Spark, no contiene la lógica SQL.

## bi-and-reporting

- **MUST** definir cada métrica una sola vez (capa semántica o modelo gold) y reutilizarla; el dashboard no recalcula negocio.
- **MUST** conectar el BI a gold/marts con una cuenta de servicio de solo lectura, nunca a raw ni a la BD transaccional.
- **MUST** propagar o respetar la clasificación: dashboards con datos `restricted` solo para roles autorizados y sin exportación libre.
- **MUST** documentar por métrica: definición, dueño, granularidad y fuente.
- **SHOULD** preferir herramientas OSS por defecto (Apache Superset o Metabase OSS, TODO-VERIFY licencia/versión); Power BI, Tableau u otros de pago solo si el cliente ya los tiene (D16).
- **SHOULD** agregar previamente (tablas resumen) en lugar de consultas pesadas sobre hechos.
- **SHOULD** versionar la definición de dashboards (export YAML/JSON) en Git.
- **MUST NOT** incrustar credenciales de BD en el dashboard ni en el repo.

## cdc-and-streaming

- **MUST** leer cambios del log de la BD (WAL/binlog) con un conector CDC; **MUST NOT** hacer polling de `updated_at` si hay que capturar borrados.
- **MUST** definir la clave de partición Kafka = clave primaria de la fila, para preservar el orden por entidad.
- **MUST** tratar el consumo como at-least-once: el destino es idempotente (upsert por PK + versión/LSN) o deduplica.
- **MUST** monitorizar el lag del slot de replicación y fijar un límite de WAL retenido; un slot abandonado llena el disco de la BD operacional.
- **MUST** publicar el esquema (Avro/JSON Schema/Protobuf) en un registro con compatibilidad `BACKWARD` como mínimo.
- **MUST** tener un plan de re-snapshot y reprocesado documentado (retención de topics, topic de DLQ).
- **MUST NOT** escribir el mismo dato en dos stores desde la aplicación (4.5): CDC lee de una única fuente de verdad.
- **SHOULD** usar el patrón outbox cuando el evento deba ser semántico y no un espejo de tablas (ver `domain-events-in-spring`).
- **SHOULD** enmascarar o excluir columnas PII en el propio conector (`column.exclude.list`) antes de que lleguen al topic.

## data-governance-and-classification

- **MUST** asignar a cada dataset un dueño de negocio (data owner) y un custodio técnico (steward) registrados en el catálogo.
- **MUST** clasificar cada columna con una etiqueta de una taxonomía cerrada: `public`, `internal`, `confidential`, `restricted` (+ marca `pii` y `special-category` cuando aplique).
- **MUST** heredar la clasificación aguas abajo: una tabla derivada tiene como mínimo la clasificación más alta de sus entradas, salvo anonimización documentada.
- **MUST** mantener la clasificación como metadatos versionados en Git (YAML junto al modelo), no solo en una UI.
- **MUST NOT** publicar en una zona de consumo (gold/marts) datos sin clasificar.
- **SHOULD** usar un catálogo OSS (p. ej. DataHub u OpenMetadata, TODO-VERIFY licencia y versión) en lugar de un producto de pago (D16).
- **SHOULD** revisar la clasificación cada trimestre y al cambiar el esquema.

## data-observability

- **MUST** monitorizar por dataset crítico cinco señales: frescura, volumen, esquema, distribución/valores nulos y fallos de tests de calidad.
- **MUST** declarar un SLO por dataset crítico (p. ej. "gold.fct_orders actualizado antes de las 07:00") con dueño y canal de aviso.
- **MUST** emitir métricas del pipeline (duración, filas leídas/escritas, reintentos) con identificador de ejecución, y enlazarlas al linaje (OpenLineage, TODO-VERIFY versión).
- **MUST** enrutar alertas al dueño del dataset, no a un canal genérico; cada alerta enlaza un runbook.
- **SHOULD** usar umbrales basados en histórico (estacionalidad) en lugar de valores fijos para volumen.
- **SHOULD** exponer el estado de datos como metadatos consultables (tabla `dataset_health`).
- **MUST NOT** incluir valores de datos personales en métricas, logs o alertas; solo contadores y agregados.
- **MUST NOT** tratar un pipeline en verde como prueba de datos correctos: puede escribir cero filas con éxito.

## data-platform-cost

- **MUST** etiquetar recursos y consultas por dominio/equipo para atribuir coste (tags de recurso, etiqueta de consulta o grupo de trabajo).
- **MUST** usar formatos columnares comprimidos (Parquet) y particionar por la columna de filtrado habitual; evitar millones de ficheros pequeños (compactar).
- **MUST** aplicar retención y ciclo de vida por zona: raw frío o expirado, gold caliente (ver `access-control-masking-and-retention`).
- **MUST** fijar un presupuesto y alerta por dominio; revisarlo mensualmente.
- **SHOULD** ajustar la frecuencia de refresco al valor de negocio (diario antes que cada minuto) y preferir cargas incrementales.
- **SHOULD** limitar `SELECT *` y escaneos sin filtro de partición; usar vistas agregadas para BI.
- **SHOULD** vigilar egress entre regiones y servicios; mantener cómputo y datos en la misma región.
- **MUST NOT** afirmar cifras de precio sin fuente y fecha: los precios del proveedor son TODO-VERIFY en la página oficial en el momento de decidir.
- **MUST NOT** introducir un servicio de pago por defecto (D16); comparar primero con alternativas OSS.

## etl-vs-elt-and-dbt

- **MUST** preferir ELT (cargar crudo, transformar en el motor analítico con SQL) cuando el destino escala; ETL solo si hay que filtrar/enmascarar antes de aterrizar (p. ej. PII, ver `gdpr-in-the-lake`).
- **MUST** conservar la capa raw inmutable; las transformaciones son reproducibles desde ella.
- **MUST** organizar modelos en capas: `staging` (1:1 con fuente, renombrado/tipado), `intermediate`, `marts` (consumo).
- **MUST** declarar tests en YAML para claves: `unique` y `not_null` en la PK, `relationships` en FKs, `accepted_values` en estados.
- **MUST** definir `unique_key` en modelos incrementales y filtrar con `is_incremental()`; **MUST** poder reconstruir con `--full-refresh`.
- **MUST NOT** usar `select *` desde `source()`; enumerar columnas.
- **MUST NOT** poner credenciales en `profiles.yml` versionado; usar variables de entorno.
- **SHOULD** documentar modelos y columnas (`description`) y exponer solo marts a BI.
- **SHOULD** usar dbt Core (OSS); dbt Cloud es de pago y requiere decisión explícita (D16).

## feature-store-and-ml-data

- **MUST** construir los conjuntos de entrenamiento con joins point-in-time (solo valores conocidos en el instante del evento) para evitar fuga de datos del futuro.
- **MUST** definir cada feature una vez (código versionado) y usar la misma definición para offline y online, evitando training-serving skew.
- **MUST** versionar datasets de entrenamiento (snapshot/tag de tabla + hash de código + parámetros) para reproducir un modelo.
- **MUST** aplicar la clasificación del dato: features derivadas de `pii` heredan la etiqueta y las reglas de RGPD (supresión, finalidad).
- **MUST NOT** usar como feature atributos protegidos o proxies sin evaluación de sesgo y base legal.
- **MUST NOT** hacer doble escritura a store online y a la BD transaccional como fuente de verdad; el online se materializa desde el offline.
- **SHOULD** usar Feast (OSS, https://docs.feast.dev/, consultada 2026-11-07) u otra solución OSS; no adoptar productos gestionados de pago por defecto (D16).
- **SHOULD** fijar TTL y frescura esperada por feature y monitorizarlas.

## gdpr-in-the-lake

- **MUST** mantener un inventario de dónde vive cada dato personal (tablas, copias, marts, features) enlazado al catálogo.
- **MUST** poder atender una solicitud de supresión (art. 17) propagándola a raw, silver, gold, features y exportaciones, salvo excepciones del art. 17(3).
- **MUST** definir base legal y finalidad por dataset; no reutilizar para fines incompatibles.
- **MUST** minimizar: no ingerir columnas personales que ningún caso de uso necesite.
- **MUST** documentar cómo se tratan los backups (expiración dentro de un plazo definido, sin restauración selectiva de datos ya suprimidos).
- **SHOULD** separar la identidad (tabla de claves) de los atributos analíticos; borrar la clave rompe el vínculo (crypto-shredding o tokenización).
- **SHOULD** usar tablas con borrado a nivel de fila (Apache Iceberg/Delta) y compactar y expirar snapshots para eliminar físicamente los ficheros.
- **MUST NOT** dar por cumplida una supresión solo con `DELETE` lógico mientras sigan snapshots, ficheros huérfanos o time travel con el dato.
- **MUST NOT** afirmar cumplimiento RGPD completo: solo "diseñado para facilitar", pendiente de revisión legal.
