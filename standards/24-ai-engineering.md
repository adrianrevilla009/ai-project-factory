# Estándares · 24-ai-engineering

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## agents-and-tool-calling

- **MUST** preferir workflow determinista antes que agente; un agente solo si el camino no se puede fijar de antemano.
- **MUST** dar a cada tool el mínimo permiso: operaciones de lectura por defecto; las de escritura en tools separadas.
- **MUST** ejecutar las tools con la identidad y permisos del usuario final, nunca con una cuenta de servicio amplia.
- **MUST** validar los argumentos que propone el modelo como entrada no confiable (tipos, rangos, listas permitidas), igual que en un endpoint REST.
- **MUST** exigir confirmación humana para acciones irreversibles o con efecto externo (pagos, borrados, envíos); ver `human-in-the-loop` (pendiente).
- **MUST** acotar el bucle: máximo de iteraciones, de tool calls, de tokens y de tiempo total; al agotarse, parar con error controlado.
- **MUST** hacer las tools de escritura idempotentes (clave de idempotencia) porque el modelo puede repetir llamadas.
- **SHOULD** describir cada tool con nombre verbal claro, descripción breve y parámetros tipados; pocas tools (decenas hacen que el modelo falle).
- **SHOULD** devolver a la tool resultados mínimos y sin datos que el usuario no deba ver; truncar salidas largas.
- **MUST** registrar cada llamada (tool, argumentos con PII redactada, resultado, usuario, traza); ver `llm-observability`.
- **MUST NOT** permitir que el texto de un resultado de tool (web, documento, email) cambie permisos o dispare tools de escritura sin confirmación (ver `prompt-injection-defense-for-agents`).

## ai-safety-and-red-teaming

- **MUST** tener un documento de alcance antes de probar: sistemas incluidos y excluidos, entornos (nunca producción con datos reales sin acuerdo), ventana temporal, responsables, canal de contacto y criterio de parada.
- **MUST** obtener autorización escrita del dueño del sistema y respetar las condiciones de uso del proveedor del modelo.
- **MUST** ejecutar las pruebas en un entorno aislado con datos sintéticos o anonimizados y credenciales de prueba de mínimo privilegio.
- **MUST** cubrir como mínimo: inyección de prompt directa e indirecta (documentos, webs, correos), fuga de prompt de sistema y de datos de otros tenants, abuso de herramientas/agentes (acciones no autorizadas), salidas dañinas o fuera de política, consumo excesivo de recursos y sesgo.
- **MUST** registrar cada caso: entrada, salida, categoría, severidad, reproducibilidad y versión de modelo/prompt.
- **MUST** convertir cada hallazgo confirmado en un caso de regresión del dataset de `llm-evals` y en una remediación con responsable y fecha.
- **MUST** tratar los resultados (que pueden contener contenido dañino o datos) como confidenciales y almacenarlos con acceso restringido.
- **SHOULD** repetir ante cada cambio de modelo, prompt, herramienta o fuente de datos, y al menos una vez por trimestre.
- **SHOULD** combinar casos manuales con generación automática de variantes, revisando los resultados a mano.
- **SHOULD** revisar el sistema frente a OWASP Top 10 for LLM Applications (edición 2025, publicada en noviembre de 2024) y frente a los requisitos de `model-risk-and-ai-act-mapping`.
- **MUST NOT** usar los resultados para atacar sistemas ajenos ni publicar técnicas de elusión contra un proveedor sin seguir su divulgación responsable.
- **MUST NOT** desactivar los controles de producción para "facilitar" la prueba y olvidar reactivarlos.

## chatbot-design

- **MUST** declarar un alcance explícito (temas permitidos, acciones permitidas, fuera de alcance) en el system prompt versionado y en la documentación del producto.
- **MUST** informar al usuario de que habla con una IA desde el primer mensaje (obligación de transparencia prevista en el AI Act; comprobar artículo y fecha con legal).
- **MUST** ofrecer escalado a un humano en cualquier momento y automáticamente tras N fallos, baja confianza o temas sensibles (queja formal, salud, legal).
- **MUST** limitar la memoria: ventana de turnos acotada, resumen en lugar de historial completo, TTL y borrado a petición (ver `pii-and-data-classification`).
- **MUST** responder "no lo sé" con enlace a fuentes cuando la recuperación no encuentra evidencia, y citar fuentes en respuestas factuales.
- **MUST** autenticar al usuario antes de exponer datos personales y aplicar autorización en las herramientas, no en el prompt (ver `llm-security`).
- **MUST NOT** guardar conversaciones completas en logs sin redacción de PII ni base legal.
- **SHOULD** aplicar rate limiting por usuario y tope de tokens por conversación (ver `token-and-cost-budgets`).
- **SHOULD** recoger feedback (pulgar arriba/abajo) y convertir fallos en casos de `llm-evals`.
- **SHOULD** diseñar degradación: si el modelo falla, mostrar canal alternativo, no un error técnico.

## classical-mlops

- **MUST** hacer reproducible el entrenamiento: versión del código, del dataset (hash o snapshot), de dependencias y semilla; guardar todo junto al artefacto.
- **MUST** mantener un registro de modelos con versión, métricas, dataset de origen, fecha y responsable; el servicio carga una versión concreta, nunca "latest".
- **MUST** separar entrenamiento, validación y prueba en el tiempo cuando los datos lo son (evitar fuga de información del futuro) y reportar métricas sobre el conjunto de prueba intacto.
- **MUST** definir un umbral de aceptación y una línea base simple (regla o modelo trivial); un modelo que no la supera no se despliega.
- **MUST** usar el mismo código de preparación de características en entrenamiento y en inferencia (una librería o servicio compartido).
- **MUST** monitorizar en servicio: latencia, errores, distribución de entradas (deriva de datos) y, cuando lleguen etiquetas, calidad real (deriva de rendimiento).
- **MUST** poder volver a la versión anterior sin reentrenar (rollback) y desplegar de forma gradual (sombra o canario).
- **SHOULD** evaluar sesgo entre grupos relevantes y documentar uso previsto y límites en una ficha del modelo (ver `model-risk-and-ai-act-mapping`).
- **SHOULD** servir modelos ligeros en proceso (p. ej. formato ONNX, comprobar runtime Java) o como servicio separado con contrato versionado.
- **SHOULD** orquestar el reentrenamiento con el orquestador de datos del proyecto (ver bloque de datos) y no con scripts manuales.
- **MUST NOT** cargar modelos serializados con `pickle` de origen no confiable: ejecuta código arbitrario al deserializar.
- **MUST NOT** entrenar con datos personales sin base legal y minimización (ver `pii-and-data-classification`).

## document-management

- **MUST** guardar el binario en almacenamiento de objetos (S3 en AWS; MinIO en local) y los metadatos en la base transaccional; nunca el binario en la BD relacional salvo ficheros diminutos justificados.
- **MUST** no duplicar la escritura de metadatos en Postgres y NoSQL (regla 4.5): una sola fuente de verdad por dato.
- **MUST** guardar por documento: id, hash SHA-256, tamaño, tipo MIME detectado, propietario/tenant, clasificación de datos, versión, fecha, clave del objeto.
- **MUST** tratar los documentos como inmutables: una modificación crea una versión nueva; el borrado es lógico y con retención definida.
- **MUST** servir descargas mediante URL prefirmada de corta duración o un endpoint que compruebe autorización por documento y tenant (ver `idor-and-object-level-authorization`).
- **MUST** cifrar en reposo (SSE-KMS en AWS; preparado para AWS, no verificado en real) y en tránsito.
- **MUST** definir retención y borrado según clasificación y normativa aplicable (borrador por confirmar con fuente oficial).
- **MUST** ordenar el flujo para evitar objetos huérfanos: subir a una clave temporal, registrar metadatos y confirmar; un job limpia temporales caducados.
- **SHOULD** generar claves de objeto opacas (UUID) y no derivarlas del nombre original, que se guarda como metadato.
- **SHOULD** activar versionado del bucket y reglas de ciclo de vida para versiones antiguas.
- **MUST NOT** exponer el bucket públicamente ni devolver rutas internas al cliente.
- **MUST NOT** usar el nombre de fichero del usuario como ruta (ver `file-upload-security`).

## guardrails-and-pii-redaction

- **MUST** clasificar los datos antes de enviarlos (ver `pii-and-data-classification`); categorías no permitidas nunca salen hacia el proveedor.
- **MUST** redactar o pseudonimizar PII en la entrada con tokens reversibles (`<PERSON_1>`) y mapa guardado solo en el servicio, si la respuesta debe re-personalizarse.
- **MUST** redactar PII en logs, trazas y datasets de evaluación; **MUST NOT** registrar prompts completos con datos reales en claro.
- **MUST** capas en orden: guardarraíl de entrada (PII, longitud, patrones de inyección), llamada, guardarraíl de salida (esquema, PII, contenido, fugas de prompt de sistema).
- **MUST** validar la salida estructurada contra esquema; si falla, reintento acotado y después error controlado, no texto libre al usuario.
- **MUST** definir el comportamiento al bloquear: mensaje neutro, código de error estable, evento de seguridad registrado (sin el contenido sensible).
- **SHOULD** combinar detectores deterministas (regex, validadores de IBAN/DNI, listas) con un detector de NER; ningún detector alcanza 100% de recall, así que medirlo con un conjunto de prueba.
- **SHOULD** usar guardarraíles del proveedor como capa adicional, nunca como única; no son reproducibles en local y deben poder desactivarse sin romper el servicio (en local, solo las capas propias).
- **MUST NOT** confiar en que "el modelo no repetirá" datos del contexto; el filtro de salida es obligatorio.
- **MUST NOT** afirmar cumplimiento RGPD/AI Act por tener filtros; es borrador por confirmar con asesoría legal (ver `model-risk-and-ai-act-mapping`).

## human-in-the-loop

- **MUST** clasificar cada acción del agente por impacto (lectura / reversible / irreversible / sobre personas) y exigir aprobación humana explícita en las dos últimas categorías.
- **MUST** separar "propuesta" de "ejecución": el modelo produce una propuesta persistida (`PENDING`), un humano la aprueba y solo entonces un componente determinista la ejecuta.
- **MUST** mostrar al revisor la evidencia (fuentes, campos extraídos, puntuación de confianza) y el diff exacto de lo que se va a ejecutar, no un resumen en lenguaje natural.
- **MUST** registrar quién aprobó, cuándo, qué versión de modelo/prompt y la decisión (aprobar / editar / rechazar) en un audit trail inmutable.
- **MUST** definir umbrales de confianza por tipo de caso; por debajo del umbral va a cola de revisión, por encima se muestrea (p. ej. auditoría aleatoria) en lugar de confiar a ciegas.
- **MUST NOT** permitir que el mismo agente apruebe su propia propuesta ni que una aprobación caduque sin revalidar si los datos cambiaron.
- **SHOULD** definir SLA y escalado de la cola de revisión y un comportamiento seguro por defecto (no ejecutar) al expirar.
- **SHOULD** medir tasa de edición/rechazo y tiempo de revisión; usarlos como señal de calidad en `llm-evals`.
- **SHOULD** diseñar para evitar el sesgo de automatización: ocultar la sugerencia hasta que el revisor forme criterio en casos de alto impacto, o exigir justificación al aprobar.

## intelligent-document-processing

- **MUST** modelar el pipeline como etapas idempotentes con estado persistido por documento: `RECEIVED -> OCR_DONE -> CLASSIFIED -> EXTRACTED -> VALIDATED -> REVIEW | APPROVED | REJECTED`.
- **MUST** conservar el original inmutable (hash SHA-256 y metadatos) y vincular cada campo extraído con su origen (página, coordenadas, motor y versión).
- **MUST** extraer a un esquema tipado (JSON Schema / record Java) y validar con reglas de negocio deterministas (sumas, formato de NIF/IBAN, fechas, rangos) tras el modelo.
- **MUST** asignar confianza por campo; por debajo del umbral va a revisión humana (ver `human-in-the-loop`). Nunca persistir campos de baja confianza como definitivos.
- **MUST** tratar el texto del documento como dato no confiable: puede contener inyección de prompt (ver `llm-security`).
- **MUST** subir ficheros con validación de tipo, tamaño y escaneo (ver `file-upload-security`).
- **MUST** clasificar y proteger PII (ver `pii-and-data-classification`) y definir retención.
- **SHOULD** procesar de forma asíncrona con cola, reintentos limitados y DLQ (ver `dlq-retries-poison-messages`).
- **SHOULD** medir por campo precisión/recall contra un conjunto etiquetado y vigilar deriva por proveedor/plantilla (ver `llm-evals`).
- **SHOULD** usar extracción por plantilla/regex cuando el formato es estable; LLM solo donde aporta.

## llm-evals

- **MUST** mantener un dataset de evaluación versionado en el repo del proyecto (`evals/datasets/*.jsonl`) con entrada, salida esperada o criterios, y etiqueta de origen.
- **MUST** separar casos de desarrollo y casos de reserva (holdout) que no se usan para ajustar prompts.
- **MUST** incluir casos adversos: entradas vacías, idioma distinto, inyección de prompt (ver `llm-security`) y casos que deben rechazarse.
- **MUST** definir métricas por tarea y umbral numérico antes de empezar a iterar (exactitud por campo, recall@k, tasa de rechazo correcto, latencia p95, coste por petición).
- **MUST** ejecutar los evals en CI ante cambios de prompt, modelo, parámetros o plantilla de recuperación y fallar si se cae por debajo del umbral.
- **MUST** fijar versión de modelo, temperatura y prompt en cada ejecución y guardar el resultado (traza) para comparar.
- **SHOULD** preferir métricas deterministas (esquema válido, igualdad, regex, recall@k) y usar juez LLM solo para criterios abiertos.
- **SHOULD** calibrar el juez LLM contra una muestra etiquetada por personas y medir su acuerdo; usar un modelo distinto al evaluado.
- **SHOULD** repetir casos no deterministas N veces y reportar media y dispersión.
- **MUST NOT** incluir datos personales reales en datasets sin anonimizar (ver `pii-and-data-classification`).
- **MUST NOT** aceptar un cambio porque "se ve mejor" en 3 ejemplos manuales.

## llm-gateway

- **MUST** centralizar el acceso a proveedores en un único punto (pasarela propia o producto open source) cuando haya más de un consumidor; los servicios no guardan claves de proveedor.
- **MUST** autenticar a cada consumidor (identidad de servicio vía Keycloak/OIDC) y atribuir cada llamada a servicio, equipo y entorno.
- **MUST** aplicar cuotas y límites de tasa por consumidor y tope de tokens por petición (ver `rate-limiting-quotas`, `token-and-cost-budgets` pendiente).
- **MUST** registrar metadatos de cada llamada (modelo, tokens, latencia, coste, versión de prompt, resultado); el contenido completo solo con redacción de PII y retención definida (ver `llm-observability`).
- **MUST** definir una lista de modelos permitidos por entorno y clasificación de datos; datos restringidos solo a proveedores aprobados.
- **SHOULD** soportar fallback entre modelos/proveedores con las mismas garantías de datos, circuit breaker y timeouts (ver `resilience`).
- **SHOULD** cachear solo respuestas deterministas y sin datos personales, con clave que incluya tenant, prompt@versión y modelo.
- **MUST NOT** crear una pasarela propia si un producto con licencia permisiva cubre el caso; evaluar antes y registrar la decisión. Sin licencias de pago por defecto (D16).
- **MUST** ejecutar las comprobaciones de guardarraíles (PII, inyección) en la pasarela o justo antes de ella (ver `guardrails-and-pii-redaction`).
- **MUST NOT** afirmar que una integración con un servicio gestionado de AWS está verificada; solo "preparado para AWS, no verificado en real". En local se usa un modelo local (por ejemplo Ollama) y NO se reproducen cuotas, IAM ni guardarraíles gestionados del proveedor.

## mcp-servers-in-java

- **MUST** elegir transporte según uso: stdio para herramientas locales de un solo usuario; HTTP (Streamable-HTTP o stateless) para servicios compartidos.
- **MUST** autenticar y autorizar todo servidor HTTP: la documentación de Spring AI avisa de que los servidores HTTP exponen un endpoint sin autenticar por defecto. Usar Spring Security con Keycloak (OIDC) y propagar la identidad al ejecutar la tool.
- **MUST NOT** exponer el servidor fuera de localhost sin autenticación, TLS y límites de tasa (ver `rate-limiting-quotas`).
- **MUST** exponer pocas tools de granularidad de caso de uso, con descripciones precisas y esquema de parámetros tipado; las de escritura separadas y con confirmación.
- **MUST** validar cada parámetro como entrada no confiable y autorizar por usuario, no por el cliente MCP.
- **MUST** tratar las descripciones de tools y los resultados como superficie de inyección: no incluir texto de terceros sin sanear en descripciones.
- **SHOULD** usar la autoconfiguración Spring AI (`spring-ai-starter-mcp-server-webmvc` o `-webflux`) con `@McpTool`/`@McpToolParam`, y fijar la versión del BOM.
- **SHOULD** versionar el contrato de tools (nombre y parámetros) y deprecar antes de retirar.
- **MUST** registrar cada invocación con usuario, tool y traza; sin PII en claro (ver `guardrails-and-pii-redaction`).
- **MUST** al consumir servidores MCP de terceros: lista de permitidos, revisión de sus tools y sin confianza implícita (ver `supply-chain`).

## model-risk-and-ai-act-mapping

- **MUST** mantener un registro de sistemas de IA (`ai-system-register`): finalidad, modelo y proveedor, datos usados, usuarios afectados, rol (proveedor / desplegador), propietario.
- **MUST** clasificar cada sistema en una categoría preliminar: práctica prohibida, alto riesgo (Anexo III o producto regulado), obligaciones de transparencia (chatbots, contenido sintético) o riesgo mínimo.
- **MUST** parar y escalar a legal si la clasificación apunta a práctica prohibida o alto riesgo; la fábrica no decide.
- **MUST** documentar riesgos de modelo: alucinación, sesgo, deriva, dependencia de proveedor, fuga de datos, abuso; con mitigación y dueño.
- **MUST** informar al usuario cuando interactúa con un sistema de IA (ver `chatbot-design`).
- **SHOULD** usar un marco reconocido (NIST AI RMF, ISO/IEC 42001) como esqueleto de gobernanza,.
- **SHOULD** versionar modelo, prompt y dataset de evaluación para poder reconstruir una decisión (ver `prompt-management`, `llm-evals`).
- **MUST NOT** afirmar "cumple el AI Act" o "certificado"; usar "mapeado a requisitos, pendiente de revisión legal".

## ocr-options

- **MUST** comprobar primero si el PDF tiene texto embebido; usar OCR solo en páginas sin él.
- **MUST** decidir el motor con una muestra etiquetada del dominio real (al menos 50 documentos de calidad variable) y métricas de `llm-evals`: tasa de error de caracteres/campos, tablas, manuscrito.
- **MUST** aislar el motor tras una interfaz (`OcrEngine`) que devuelva texto, confianza, página y coordenadas, para poder cambiarlo.
- **MUST** registrar motor y versión por documento (trazabilidad).
- **MUST** evaluar privacidad antes de enviar documentos a un servicio externo: clasificación de datos, región, retención y acuerdo con el proveedor (ver `pii-and-data-classification`).
- **MUST** preprocesar de forma explícita (rotación, deskew, resolución ~300 dpi) y medir su efecto; no asumirlo.
- **SHOULD** usar Tesseract (licencia Apache 2.0, ejecución local, sin coste por página) como opción por defecto de la fábrica para texto impreso limpio; comprobar versión y paquetes de idioma al fijar el proyecto.
- **SHOULD** valorar un servicio gestionado (p. ej. Amazon Textract, preparado para AWS, no verificado en real) o un modelo de visión cuando haya tablas, formularios o manuscrito y los datos lo permitan.
- **SHOULD** limitar páginas por documento, tamaño y tiempo por página; procesar en cola asíncrona.
- **MUST NOT** tratar la confianza del motor como probabilidad calibrada sin comprobarlo.
- **MUST NOT** introducir un servicio de pago por defecto (D16); si se elige, documentarlo en un ADR con coste estimado.

## prompt-management

- **MUST** tratar los prompts como código: ficheros en el repo (`src/main/resources/prompts/*.st` o similar), con revisión en PR, no strings dispersos ni editables en caliente sin trazabilidad.
- **MUST** usar plantillas con variables nombradas; **MUST NOT** construir prompts concatenando entrada de usuario o texto recuperado en el prompt de sistema.
- **MUST** versionar cada prompt (`id` + `version`) y registrar la versión usada en cada llamada (log/traza, ver `llm-observability`).
- **MUST** tener tests de regresión por prompt: casos dorados con aserciones sobre estructura y contenido clave, ejecutables sin red (modelo falso) y, aparte, una suite de evaluación con modelo real (ver `llm-evals`, pendiente).
- **MUST** separar instrucciones (sistema) de datos (usuario, documentos) con delimitadores y una declaración explícita de que son datos.
- **SHOULD** pedir salida estructurada con esquema (ver `structured-outputs-and-streaming`, pendiente) en lugar de parsear texto libre.
- **SHOULD** fijar modelo y parámetros (`temperature`, `max_tokens`) junto al prompt, porque el comportamiento depende de ambos.
- **MUST NOT** incluir secretos, datos personales reales ni detalles de infraestructura en prompts.
- **MUST** poder hacer rollback de un prompt sin redeploy completo solo si existe un registro versionado con aprobación; si no, rollback = revertir PR.

## rag-architecture

- **MUST** separar dos pipelines: ingesta (offline, idempotente, reintentable) y consulta (online, con timeout).
- **MUST** guardar con cada chunk metadatos: `source_id`, `version`, `acl` (grupos autorizados), `tenant`, `updated_at`, ubicación (página/sección).
- **MUST** filtrar por `acl` y `tenant` en la consulta al vector store, antes de que el texto llegue al LLM; nunca filtrar después de generar.
- **MUST** versionar el modelo de embeddings junto al índice; cambiar de modelo implica reindexar entero (los vectores no son comparables).
- **MUST** exigir citas: la respuesta incluye `source_id` y ubicación; si no hay contexto relevante, responder "no lo sé" en lugar de inventar.
- **SHOULD** chunking por estructura (secciones/párrafos) con solapamiento pequeño, y medir tamaños con datos reales, no por defecto.
- **SHOULD** recuperación híbrida (léxica + vectorial) y reranking si la precisión lo exige.
- **MUST NOT** tratar el contenido recuperado como instrucciones: va delimitado y declarado como dato (ver `prompt-injection-defense-for-agents`).
- **MUST** evaluar con un conjunto dorado (recall@k de recuperación y fidelidad de respuesta) antes de cambiar chunking, modelo o k (ver `llm-evals`, pendiente).
- **MUST NOT** doble escritura: el índice vectorial es derivado y reconstruible desde la fuente de verdad.

## rag-over-enterprise-docs

- **MUST** heredar los permisos de la fuente: capturar la ACL original en la ingesta y re-sincronizarla de forma periódica; un cambio de permisos debe reflejarse en el índice en un SLA definido.
- **MUST** soportar borrado y expiración: cuando el documento se elimina en la fuente, se eliminan sus chunks y vectores (derecho de supresión, ver `gdpr-in-the-lake`).
- **MUST** clasificar el corpus antes de indexar (ver `pii-and-data-classification`); no indexar categorías prohibidas y redactar PII que no deba llegar al modelo (ver `guardrails-and-pii-redaction`).
- **MUST** registrar por documento: hash de contenido, versión, estado de parsing, errores; la ingesta es incremental por hash, no reprocesa todo.
- **MUST** poner OCR/parsing de PDFs escaneados en una cola con revisión de calidad; un parsing malo envenena la recuperación en silencio.
- **SHOULD** conservar estructura (títulos, tablas como texto estructurado, número de página) para citas navegables.
- **SHOULD** deduplicar versiones: indexar solo la vigente y marcar las obsoletas con `valid_to`.
- **MUST NOT** copiar el documento completo al vector store si basta un puntero a la fuente + chunks; el original sigue en su sistema.
- **MUST NOT** usar una cuenta de servicio con acceso total para responder a usuarios sin aplicar el filtro de ACL del usuario final.
- **MUST** tratar el texto de los documentos como no confiable (prompt injection indirecta, ver `prompt-injection-defense-for-agents`).

## spring-ai-and-langchain4j

- **MUST** elegir UN framework por servicio y registrar la decisión en un ADR del proyecto (criterios: integración Spring Boot, madurez de la API, cobertura de proveedores y vector stores necesarios).
- **SHOULD** preferir Spring AI en servicios Spring Boot (autoconfiguración, `ChatClient`, advisors, observabilidad Micrometer); LangChain4j si se necesita `AiServices` declarativo o cobertura que Spring AI no tenga.
- **MUST** fijar la versión del BOM del framework en `dependencyManagement`; ambos evolucionan rápido y sus APIs cambian entre versiones menores (comprobar versión vigente al arrancar el proyecto).
- **MUST** encapsular el framework tras un puerto propio (`interface AnswerGenerator`) en la capa de aplicación; el dominio no importa `org.springframework.ai` ni `dev.langchain4j`.
- **MUST** configurar timeouts, reintentos acotados y modelo/temperatura por propiedades, no en código.
- **MUST** leer claves del proveedor desde el gestor de secretos (ver `secrets-management`), nunca de `application.yml`.
- **MUST NOT** mezclar ambos frameworks en el mismo servicio.
- **SHOULD** probar con un `ChatModel` falso en tests unitarios y con un modelo local (Ollama) solo en tests de integración marcados.
- **MUST NOT** usar Lombok (D27).

## structured-outputs-and-streaming

- **MUST** definir un esquema (JSON Schema o record Java) por cada salida consumida por código y validar la respuesta contra él antes de usarla, aunque el proveedor ofrezca modo estructurado.
- **SHOULD** usar la función nativa de salida estructurada del proveedor cuando exista (en la API de Claude: `output_config.format` con `type: "json_schema"`, y `strict: true` en herramientas; verificado en la documentación de Claude el 2026-11-08: GA desde 2026-01-29; la disponibilidad por modelo y por proveedor de nube se comprueba al elegirlos).
- **MUST** tratar el JSON generado como entrada no confiable: validar tipos, rangos y longitudes; reglas de negocio deterministas después (ver `intelligent-document-processing`).
- **MUST** gestionar fallos: truncado por `max_tokens`, rechazo del modelo, JSON inválido. Reintentar como máximo 1-2 veces con el error de validación; después, error controlado o revisión humana.
- **MUST** usar `enum` y campos cerrados (`additionalProperties: false`) para clasificaciones; incluir un valor explícito `unknown`.
- **MUST** en streaming: no parsear JSON parcial como definitivo; acumular hasta el evento de fin o usar un parser incremental tolerante y validar al cerrar.
- **MUST** en streaming: propagar cancelación del cliente al proveedor (cerrar el flujo) y poner timeouts de inactividad y totales.
- **MUST** enviar por SSE eventos tipados (`delta`, `done`, `error`) y filtrar con guardrails antes de mostrar si hay contenido sensible (ver `guardrails-and-pii-redaction`).
- **SHOULD** versionar el esquema y mantenerlo compatible hacia atrás (campos nuevos opcionales).
- **MUST NOT** ejecutar ni interpolar en SQL, shell o HTML ningún campo de la salida sin tratamiento (ver `llm-security`).

## token-and-cost-budgets

- **MUST** fijar `max_tokens` (salida) explícito en cada llamada y un tope de tokens de entrada; truncar o resumir el contexto antes de superarlo.
- **MUST** medir tokens de entrada y salida reales de cada respuesta (los devuelve la API) y registrarlos con `tenant`, `feature` y `model` como etiquetas de baja cardinalidad (ver `llm-observability`).
- **MUST** definir presupuesto por petición, por usuario/tenant y por día; al agotarlo, degradar (modelo menor, respuesta corta) o rechazar con error claro, nunca seguir sin límite.
- **MUST** poner tope a bucles de agentes: máximo de iteraciones, de llamadas a herramientas y de tokens acumulados por tarea.
- **MUST** pasar todas las llamadas por el `llm-gateway` para aplicar cuotas y registrar el gasto en un único sitio.
- **MUST** configurar alertas de gasto (umbral diario y salto respecto a la media) y un corte duro.
- **SHOULD** usar caché de prompt del proveedor para prefijos largos y estables, y caché de respuestas para entradas idénticas sin datos personales.
- **SHOULD** enrutar tareas simples a un modelo pequeño y reservar el grande para tareas difíciles, medido con `llm-evals`.
- **SHOULD** estimar el coste con la tabla de precios del proveedor leída de configuración, con fecha de vigencia.
- **MUST NOT** codificar precios en el código ni asumirlos estables; cambian con frecuencia.
- **MUST NOT** enviar documentos completos si basta un fragmento recuperado.

## training-data-licensing-and-provenance

- **MUST** mantener un registro de procedencia por conjunto de datos: origen, fecha de obtención, licencia o base legal, titular, finalidad permitida, restricciones (uso comercial, atribución, derivadas) y responsable.
- **MUST** verificar que la licencia o el contrato permiten el uso previsto (entrenar, afinar, redistribuir el modelo, uso comercial) antes de incorporar el dato; ante duda, excluirlo hasta aclararlo.
- **MUST** no usar datos de clientes para entrenar sin cláusula contractual o consentimiento que lo permita y sin limitar la finalidad.
- **MUST** clasificar datos personales y aplicar minimización, anonimización o seudonimización antes de entrenar (ver `pii-and-data-classification`); definir la base legal (RGPD, borrador por confirmar).
- **MUST** respetar señales de exclusión del origen (términos de uso, `robots.txt`, avisos de reserva de derechos) y no hacer scraping de fuentes que lo prohíban.
- **MUST** versionar el dataset con hash e identificar qué versión entrenó cada modelo (ver `classical-mlops`).
- **MUST** poder retirar datos: si un titular ejerce sus derechos o caduca una licencia, saber qué modelos e índices se ven afectados y planificar reindexado o reentrenamiento.
- **SHOULD** preferir datos propios, de licencia abierta compatible (CC0, CC-BY, Apache-2.0 según el caso) o sintéticos generados con modelos cuyas condiciones permitan ese uso (comprobar por proveedor).
- **SHOULD** mantener la lista de licencias aceptadas y rechazadas por el proyecto y una revisión legal para las dudosas.
- **SHOULD** revisar el dato sintético: puede heredar restricciones del modelo generador y sesgos.
- **MUST NOT** mezclar sin etiquetar datos con licencias incompatibles en un mismo conjunto.
- **MUST NOT** asumir que un dato "público" en la web es de uso libre.

## vector-store-selection

- **MUST** empezar por la opción más simple que cubra el volumen: pgvector en el Postgres existente si hay menos de unos pocos millones de vectores (umbral orientativo, medir en el proyecto).
- **MUST** decidir con una prueba medida sobre datos propios: recall@k frente a búsqueda exacta, latencia p95 y coste (ver `llm-evals`).
- **MUST** no duplicar el dato maestro: el vector es un derivado reconstruible de la fuente; si la fuente es Postgres y el vector va a otro motor, usar outbox/CDC y declararlo derivado (regla 4.5, sin doble escritura).
- **MUST** guardar con cada vector: id de la fuente, versión del modelo de embeddings, dimensión y tenant; un cambio de modelo exige reindexar todo.
- **MUST** aplicar filtros de autorización (tenant, permisos del documento) en la propia consulta vectorial, no después de recuperar.
- **MUST** elegir la métrica de distancia que corresponde al modelo (coseno, producto interno o L2) y usar el mismo operador que el índice.
- **SHOULD** usar índice HNSW en pgvector para consultas con buena relación velocidad/recall (más memoria y build lento) e IVFFlat si importa más el tiempo de construcción; comprobar versión de pgvector instalada.
- **SHOULD** valorar OpenSearch (k-NN) cuando ya se opera para búsqueda de texto y se necesita búsqueda híbrida (léxica + vectorial) o escala horizontal; preparado para AWS, no verificado en real.
- **SHOULD** medir recall tras cambios de parámetros del índice (`ef_search`, `lists`/`probes`).
- **MUST NOT** adoptar un servicio gestionado de pago por defecto (D16) sin ADR con coste.
- **MUST NOT** indexar PII sin clasificación y política de borrado: borrar la fuente implica borrar sus vectores.
