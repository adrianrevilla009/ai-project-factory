# Estándares · 14-secrets-and-config

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## audit-and-break-glass

- **MUST** habilitar al menos dos audit devices (p. ej. `file` y `syslog`/`socket`) en cada clúster: si ninguno puede escribir, Vault rechaza la petición.
- **MUST** enviar los logs de auditoría fuera del nodo Vault (agregador de logs con retención y acceso restringido); quien administra Vault no puede borrarlos.
- **MUST** monitorizar fallos de escritura del audit device y alertar: es indisponibilidad del servicio, no un detalle.
- **MUST NOT** usar `log_raw` salvo diagnóstico puntual aprobado: expone valores sin hash.
- **MUST** revocar el root token tras el bootstrap; generar uno nuevo solo con `vault operator generate-root` y quórum de claves, y revocarlo al terminar.
- **MUST** definir break-glass como procedimiento documentado: política `break-glass` nominal, TTL corto, activación con doble aprobación, alerta inmediata al activarse y revisión posterior obligatoria.
- **MUST** repartir las claves de unseal/recovery entre custodios distintos (Shamir) y registrar quién las custodia, sin guardarlas juntas.
- **SHOULD** ensayar el break-glass al menos semestralmente en un entorno no productivo.
- **SHOULD** alertar sobre uso de rutas sensibles (`sys/audit`, `sys/policies`, `sys/generate-root`).

## auth-methods

- **MUST** autenticar pods con el método `kubernetes` (ServiceAccount JWT), un rol por servicio y namespace, con `bound_service_account_names` y `bound_service_account_namespaces` explícitos (nunca `*`).
- **MUST** autenticar humanos con OIDC contra Keycloak (D12) y mapear grupos a políticas; **MUST NOT** crear usuarios `userpass` compartidos.
- **MUST** autenticar CI con JWT/OIDC (token de GitHub Actions) acotando `bound_claims` a repositorio y rama/entorno; **MUST NOT** guardar tokens Vault estáticos como secreto de CI.
- **SHOULD** limitar AppRole a casos sin identidad de plataforma; el `secret_id` debe ser de un solo uso y con TTL corto, y el `role_id` no es secreto pero tampoco se publica.
- **MUST** asignar `token_ttl` corto (p. ej. 15 min–1 h), `token_max_ttl` acotado y `token_policies` mínimas por rol; **MUST NOT** usar tokens sin expiración ni el root token salvo bootstrap.
- **MUST** usar `token_bound_cidrs` donde la red lo permita y `token_num_uses` para tokens de tarea única.
- **SHOULD** deshabilitar métodos sin uso y auditar `sys/auth`.
- **MUST** tener un clúster Vault por región: cada uno registra sus propios métodos y roles; la configuración se aplica desde el mismo código Terraform, no por replicación.

## config-by-environment

- **MUST** seguir D11: la configuración no secreta vive en Git (overlays por entorno, aplicados por GitOps); los secretos viven en Vault y nunca en Git.
- **MUST** mantener el artefacto inmutable: la misma imagen se promueve entre entornos; solo cambian configuración y secretos.
- **MUST** separar por capas: `application.yml` (defectos seguros) < overlay de entorno < overlay de región < secretos inyectados. Solo se sobrescribe lo necesario.
- **MUST** referenciar secretos con placeholders (`${DB_PASSWORD}`) o ficheros montados; el valor lo inyecta Vault (ver `injection-patterns`).
- **MUST** validar la configuración al arrancar (`@Validated` + fallo rápido) para que un valor ausente rompa el despliegue, no la primera petición.
- **MUST NOT** usar perfiles de Spring para esconder diferencias de comportamiento de negocio; los perfiles solo seleccionan infraestructura.
- **MUST NOT** poner valores `prod` por defecto en el repositorio de código del servicio; el repo de entornos (GitOps) es la fuente.
- **SHOULD** que cada cambio de configuración pase por PR con revisión y quede auditado en Git.
- **SHOULD** documentar cada clave con propietario, valores permitidos y si es sensible.

## deployment-ha

- **MUST** desplegar Vault OSS con almacenamiento integrado Raft, 3 nodos (5 si el tier lo exige), uno por AZ (D10, ADR-0010). Un nodo perdido de 3 mantiene quórum; dos no.
- **MUST** usar un clúster Vault **independiente por región**. **MUST NOT** asumir replicación de rendimiento/DR: es función Enterprise y de pago (D16). Si se documenta, solo como variante opcional.
- **MUST** configurar auto-unseal con KMS de la propia región (`seal "awskms"` con `region` y `kms_key_id`); la identidad de Vault (IRSA/rol de instancia) solo necesita `kms:Encrypt`, `kms:Decrypt`, `kms:DescribeKey` sobre esa clave.
- **MUST NOT** poner `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` en el stanza del seal ni en el repo.
- **MUST** custodiar las recovery keys (Shamir 5/3) con personas distintas, fuera de Vault y fuera del repo; el root token inicial se revoca tras el bootstrap.
- **MUST** habilitar TLS en listener API (8200) y clúster (8201); `tls_disable = true` está prohibido fuera de `dev`.
- **MUST** programar snapshots Raft (`vault operator raft snapshot save`) a un bucket de la misma región con cifrado, y ensayar la restauración.
- **SHOULD** usar Raft Autopilot para limpieza de nodos muertos y actualizaciones controladas.
- **SHOULD** fijar `topologySpreadConstraints` por zona y `PodDisruptionBudget` `maxUnavailable: 1`.
- **SHOULD** registrar la licencia: Vault es BUSL, OpenBao es la alternativa abierta (ADR-0031); TODO-VERIFY licencia de la versión fijada con revisión legal.

## dynamic-database-credentials

- **MUST** usar el motor `database` con un usuario "root" de Vault de privilegios mínimos (crear/alterar/borrar roles de aplicación) y **MUST** rotarlo con `rotate-root` tras configurarlo.
- **MUST** definir un rol Vault por servicio y permiso (`orders-rw`, `orders-ro`) con `default_ttl` corto (p. ej. 1 h) y `max_ttl` acotado, con `creation_statements` que concedan solo los GRANT necesarios.
- **MUST** preferir credenciales dinámicas; usar **roles estáticos** (rotación de un usuario fijo) solo si el sistema no tolera usuarios efímeros (migraciones, herramientas legadas).
- **MUST** que la aplicación renueve el lease o reabra el pool al expirar: el pool de conexiones (HikariCP) debe soportar credenciales rotadas (ver `rotation-and-leases`).
- **MUST** apuntar la conexión de Vault al endpoint de **escritura** del clúster; Vault no puede crear roles en una réplica de solo lectura.
- **TRAMPA, orden en failover (Aurora Global, brief §9):** la secundaria es de solo lectura hasta promoverse. El runbook **MUST** fijar el orden: 1) promover la BD secundaria, 2) actualizar `connection_url` y activar/validar el motor de BD del Vault de esa región, 3) escalar las apps. Hacerlo al revés deja a Vault sin poder emitir credenciales.
- **MUST** tener en cada región su propio Vault y su propio motor de BD (D10): no hay replicación de leases entre clústeres. Las credenciales emitidas en la región caída se consideran perdidas y se recrean.
- **SHOULD** dejar una credencial de emergencia (break-glass, pendiente `audit-and-break-glass`) para recuperar acceso si el motor falla durante el failover.
- **MUST NOT** emitir credenciales con `SUPERUSER` ni con propiedad de esquemas para servicios de aplicación.

## envelope-encryption-and-kms

- **MUST** usar cifrado de sobre: una clave de datos (DEK) por objeto/registro cifra el dato; una clave maestra (KEK) cifra la DEK. Se guarda la DEK cifrada junto al dato.
- **MUST** respetar ADR-0010: Vault Transit NO comparte material de claves entre regiones (clúster independiente por región). Los datos leídos desde ambas regiones MUST usar claves multi-región de KMS.
- **MUST** usar, en AWS, una clave multi-región (primaria + réplicas) con políticas de clave y alias gestionados por región; preparado para AWS, no verificado en real. En local no se reproduce KMS real: usar un adaptador de prueba con clave falsa (`changeme`).
- **MUST** usar AEAD (AES-GCM) con contexto de cifrado (encryption context) ligado al tenant/registro, para impedir copiar un blob a otro registro.
- **MUST NOT** persistir DEK en claro, loguearla ni reutilizar una misma DEK para volúmenes grandes sin límite.
- **MUST NOT** implementar primitivas propias; usar la librería de cifrado de sobre del proveedor o Tink/JCA según `crypto-tls-mtls-key-rotation`.
- **MUST** habilitar rotación automática de la KEK y almacenar el identificador de versión/clave con el texto cifrado para poder descifrar histórico.
- **SHOULD** usar Vault Transit cuando los datos son mono-región y se quiere evitar que la clave salga de Vault.
- **SHOULD** minimizar llamadas a KMS cacheando DEK descifradas con TTL corto y límite de uso.
- **SHOULD** aislar el acceso: la identidad de la aplicación solo `Encrypt/Decrypt/GenerateDataKey` sobre su clave.

## feature-flags-openfeature

- **MUST** acceder a los flags a través de la API de OpenFeature (estándar abierto, SDK Java) y no del SDK de un proveedor concreto, para poder cambiar de provider sin tocar el código de negocio.
- **MUST** elegir un provider sin licencia de pago por defecto (D16); fichero/ConfigMap o un servidor OSS compatible con OpenFeature. TODO-VERIFY provider concreto y versión.
- **MUST** pasar siempre un valor por defecto seguro en cada evaluación: si el provider cae, el sistema se comporta como "flag apagado".
- **MUST** tipificar y nombrar los flags (`orders.new-pricing.enabled`) con propietario, fecha de creación y fecha de retirada prevista.
- **MUST** clasificar cada flag: release (vida corta), ops/kill switch, experimento o permiso; solo los de release y experimento caducan.
- **MUST** eliminar el flag y el código muerto al completar el despliegue; un flag release sin retirar tras su fecha es deuda.
- **MUST NOT** meter PII ni secretos en el contexto de evaluación; usar identificadores opacos.
- **MUST NOT** anidar flags ni condicionar la corrección de datos a su estado sin plan de migración.
- **SHOULD** evaluar el flag en el borde del caso de uso, no en capas de dominio; inyectar un puerto `FeatureToggles`.
- **SHOULD** registrar cambios de flags en la auditoría y con un hook de OpenFeature para métricas/trazas.
- **SHOULD** probar ambas ramas del flag en tests.

## injection-patterns

- **SHOULD** usar **Vault Secrets Operator (VSO)** por defecto: sincroniza a `Secret` de Kubernetes mediante CRDs (`VaultStaticSecret`, `VaultDynamicSecret`) sin sidecar. Es la opción más simple de operar.
- **SHOULD** usar **Agent Injector** (sidecar) cuando se necesita renovación de leases y plantillas de fichero sin `Secret` de K8s; coste: un contenedor extra por pod.
- **SHOULD** usar **CSI Provider** cuando no se quiere persistir el valor en etcd y basta montar un volumen efímero; limitación: rotación y sincronización a variables de entorno más pobre. TODO-VERIFY comportamiento de rotación en la versión fijada.
- **MUST** documentar la elección por servicio en un ADR corto; **MUST NOT** mezclar patrones sin motivo.
- **MUST** preferir montar secretos como **ficheros** y leerlos con `spring.config.import=optional:configtree:/vault/secrets/`; evitar variables de entorno (se filtran en volcados y `/proc`).
- **MUST** que el cifrado de `Secret` en etcd (KMS provider) esté activo si se usa VSO; sin él, el secreto queda en claro en etcd. TODO-VERIFY configuración EKS.
- **MUST** que cada servicio use su ServiceAccount y rol (`auth-methods`); **MUST NOT** compartir un rol entre namespaces.
- **MUST** que la app tolere el cambio del secreto (relectura o reinicio controlado; en VSO, `rolloutRestartTargets`).
- **MUST NOT** registrar valores de secretos en logs, `toString()` ni Actuator (`management.endpoint.env.show-values=NEVER`).
- **MUST NOT** poner un token Vault de larga vida en un `Secret` o `ConfigMap`.

## pki-and-cert-issuance

- **MUST** mantener la CA raíz fuera de línea (o en un Vault aislado) y firmar solo CA **intermedias**; el Vault operativo solo guarda la intermedia.
- **MUST** una intermedia por región (D10: clústeres independientes), firmada por la misma raíz, de modo que un cliente confíe en ambas regiones con una sola raíz.
- **MUST** definir roles PKI acotados: `allowed_domains`, `allow_subdomains`, `max_ttl` corto (horas/días), `key_type`/`key_bits` modernos (RSA 2048+ o EC P-256+), `enforce_hostnames=true`.
- **MUST NOT** crear roles con `allow_any_name=true` ni `allow_localhost` en producción.
- **SHOULD** emitir certificados de hoja de vida corta y renovarlos automáticamente (cert-manager con `ClusterIssuer` de tipo Vault, o agente/VSO) en lugar de revocar.
- **MUST** publicar CRL/OCSP o aceptar que la revocación es débil y compensarlo con TTL corto; configurar `issuing_certificates` y `crl_distribution_points` con la URL de la región.
- **SHOULD** activar `tidy` automático para purgar certificados expirados del almacenamiento Raft.
- **MUST NOT** exportar ni guardar claves privadas de la CA intermedia en el repo ni en logs.
- **MUST** documentar la rotación de la intermedia (cross-signing) antes de que caduque.

## policies

- **MUST** escribir una política por servicio/función, con `path` concretos y las `capabilities` mínimas (`read` para leer; evitar `create`/`update`/`delete`/`sudo`).
- **MUST NOT** usar `path "*"`, `path "secret/*"` con `["create","read","update","delete","list","sudo"]`, ni políticas con `sudo` fuera de administración.
- **MUST** estructurar paths por entorno y servicio (`kv/data/<env>/<service>/*`); en KV v2 la política va sobre `data/` y `metadata/`, no sobre el path lógico.
- **SHOULD** usar templating de identidad (`{{identity.entity.aliases.<accessor>.metadata.service_account_namespace}}`) para una sola política reutilizable.
- **MUST** separar políticas de lectura de secretos, de emisión (`database/creds/*`, `pki/issue/*`, `transit/encrypt/*`) y de administración.
- **MUST** gestionar las políticas como código (Terraform `vault_policy`), revisadas en PR, y aplicarlas idénticas en cada clúster regional.
- **MUST NOT** conceder a una aplicación acceso a `sys/*`, `auth/*` ni a `transit/keys/*` (gestión de claves).
- **SHOULD** probar con `vault token capabilities <token> <path>` y tests negativos (debe fallar lo no concedido).
- **SHOULD** reservar `root` y la política administrativa para break-glass (ver audit-and-break-glass, pendiente de escribir).

## rotation-and-leases

- **MUST** dar a todo secreto un TTL: `default_ttl` corto y `max_ttl` acotado por motor/rol. **MUST NOT** emitir leases sin caducidad.
- **MUST** que el cliente renueve el lease antes de que expire (hacia ~2/3 del TTL) y, al llegar a `max_ttl`, solicite credenciales nuevas en vez de fallar.
- **MUST** que el pool de conexiones soporte la rotación: crear conexiones con credenciales nuevas y drenar las antiguas (HikariCP: `maxLifetime` menor que el TTL del lease, menos margen).
- **MUST** coordinar el TTL de la credencial con `maxLifetime` y con el tiempo de arranque de la app; un TTL menor que el arranque causa bucles de fallo.
- **SHOULD** usar revocación por prefijo (`vault lease revoke -prefix`) en respuesta a incidentes, y comprobar su efecto en la BD.
- **MUST** rotar secretos estáticos (API keys de terceros, roles estáticos de BD) con periodo definido y propietario; la rotación **MUST** ser automática o con runbook probado.
- **MUST** monitorizar: leases activos, fallos de renovación, expiraciones inminentes, errores de autenticación tras rotar.
- **MUST** asumir que, tras un failover regional (D10), los leases del Vault caído no existen en el otro: las apps piden credenciales nuevas al Vault local (ver `dynamic-database-credentials` para el orden BD, luego motor).
- **SHOULD** evitar rotar `root` de BD y claves de unseal en horas punta; planificar ventanas.
- **MUST NOT** usar rotación como sustituto de revocar un secreto comprometido: revocar primero.

## secret-scanning-and-leak-response

- **MUST** ejecutar un escáner de secretos con licencia OSS (p. ej. gitleaks, MIT) en pre-commit y en CI sobre cada PR; el job de CI bloquea el merge.
- **MUST** escanear también el histórico completo al adoptar el repositorio y de forma periódica, con baseline versionado para hallazgos aceptados y revisados.
- **MUST** mantener una configuración de reglas del proyecto (`.gitleaks.toml`) con reglas propias de los formatos internos de token.
- **MUST** tratar cualquier hallazgo real como comprometido: 1) revocar/rotar primero, 2) revisar los logs de auditoría por uso indebido, 3) limpiar el historial si procede, 4) post-mortem y regla de detección nueva. Borrar el commit no basta.
- **MUST NOT** desactivar el escáner con `SKIP=` ni con allowlists amplias; las excepciones llevan justificación y caducidad en PR.
- **MUST** usar en ejemplos y tests literales falsos con `example` o `changeme`, y registrarlos en la allowlist estrecha por ruta.
- **MUST** tener runbook de fuga con responsable, canal y plazos (SLA según `vulnerability-sla-and-incident-response`).
- **SHOULD** activar el secret scanning/push protection de la plataforma Git si está disponible sin coste, además del escáner propio.
- **SHOULD** escanear también imágenes, artefactos de build y logs de CI.
- **SHOULD** medir tiempo de rotación tras detección y número de falsos positivos.

## spring-cloud-config-module

- **MUST** partir de GitOps + Vault y documentar por escrito en un ADR del proyecto por qué no basta antes de añadir Config Server.
- **MUST** justificar con al menos uno de: cambio de configuración en caliente sin redespliegue (con `/actuator/refresh` o bus), muchos servicios no Kubernetes, o equipos que ya operan Config Server.
- **MUST NOT** guardar secretos en el repositorio Git del Config Server; usar el backend Vault del servidor o inyección por Vault (TODO-VERIFY backend y propiedades en la versión de Spring Cloud fijada).
- **MUST** proteger el servidor: autenticación entre servicios (mTLS o OAuth2), sin endpoints abiertos, y cifrado de transporte.
- **MUST** tratarlo como componente de plataforma crítico: al menos 2 réplicas, healthchecks y alerta, porque su caída bloquea arranques.
- **MUST** configurar los clientes con fallo rápido y reintentos acotados (`spring.config.import` con `configserver:`), y valores por defecto seguros.
- **SHOULD** limitar `refresh` a propiedades marcadas como refrescables; el resto exige reinicio.
- **SHOULD** versionar la configuración por etiqueta/rama equivalente al entorno y pasar por PR.
- **MUST NOT** convertirlo en punto único de fallo global: un Config Server por entorno/región, no uno compartido.

## transit-encryption

- **TRAMPA (brief §9, D10):** con un clúster Vault independiente por región, **el material de claves de Transit no se comparte**. Un `ciphertext` `vault:v1:...` generado en la región A **no** puede descifrarse en la B. **MUST NOT** diseñar datos replicados entre regiones cifrados con Transit.
- **MUST** reservar Transit para datos cuya lectura es local a una región (o aislados por celda), o como capa adicional sobre datos que ya usan sobre-cifrado KMS.
- **MUST NOT** resolver la limitación exportando claves (`exportable=true`) para copiarlas entre clústeres, ni asumiendo replicación Enterprise (D16, no se asume).
- **MUST** una clave por propósito (`orders-pii`), nunca una clave global; `deletion_allowed=false` por defecto.
- **MUST** rotar claves con `transit/keys/<k>/rotate` y fijar `min_decryption_version`; tras rotar, rewrapear los datos antiguos (`transit/rewrap`) de forma gradual.
- **SHOULD** usar `convergent_encryption` solo si se necesita búsqueda por igualdad, aceptando la fuga de igualdad.
- **MUST** pasar el contexto (`context`) con claves derivadas cuando se separan inquilinos.
- **MUST** guardar el ciphertext junto con la versión de clave (ya viene en el prefijo) y registrar qué región lo produjo.
- **MUST NOT** conceder a la app permisos de gestión de claves (ver `policies`).

## vault-and-keycloak-dr

- **MUST** asumir que Vault OSS no incluye replicación de DR entre clústeres (es función Enterprise, fuera de alcance por D10/D16); la recuperación se basa en snapshots Raft y reconstrucción. TODO-VERIFY contra la documentación vigente de la versión fijada.
- **MUST** programar snapshots Raft (`vault operator raft snapshot save`) y copiarlos cifrados a almacenamiento fuera del clúster y de la región (en AWS, S3 con KMS: preparado para AWS, no verificado en real).
- **MUST** definir RPO = intervalo de snapshot y RTO medido, y ensayar la restauración en un clúster limpio al menos trimestralmente.
- **MUST** proteger por separado las claves de unseal/recovery y el material de auto-unseal: un snapshot sin ellos no sirve.
- **MUST** tener un runbook de pérdida total de región: Vault de la región superviviente no tiene los secretos del otro; los secretos fuente deben reconstruirse desde GitOps (config) y desde sistemas origen (credenciales dinámicas se regeneran).
- **MUST** respaldar la base de datos de Keycloak (realms, usuarios, clientes) con el mismo rigor que los datos de negocio, y mantener los realms exportados como código (`kc.sh export` o configuración declarativa) sin secretos reales.
- **MUST NOT** restaurar un snapshot en un clúster productivo sin segundo aprobador.
- **SHOULD** tratar el arranque en frío (Vault y Keycloak caídos) como dependencia circular a documentar: qué servicios arrancan sin ellos.
- **SHOULD** versionar la matriz "qué NO se reproduce en local": el auto-unseal con KMS y el backup a S3 no se reproducen en local.
