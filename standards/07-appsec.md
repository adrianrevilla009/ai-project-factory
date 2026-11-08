# Estándares · 07-appsec

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## asvs-mapping

- **MUST** declarar el nivel ASVS objetivo por servicio (L1 mínimo; L2 por defecto si trata datos personales o autenticación; L3 solo con justificación de riesgo) en un ADR.
- **MUST** mantener una matriz capítulo -> requisito aplicable -> evidencia (test, config o ADR) -> estado.
- **MUST** marcar como "no aplica" cada requisito descartado, con motivo; no dejar celdas vacías.
- **MUST** convertir los requisitos aplicables en criterios de aceptación de las historias afectadas (login, sesión, validación, API).
- **SHOULD** priorizar capítulos de autenticación, control de acceso, validación, criptografía y registro.
- **MUST NOT** afirmar "cumple ASVS L2" sin evidencia por requisito; usar "cobertura ASVS L2: N de M requisitos con evidencia".
- **SHOULD** referenciar los identificadores con la versión explícita (p. ej. `v5.0.0-x.y.z`) para que no cambien de significado.

## audit-trail-and-security-logging

- **MUST** registrar como mínimo: login correcto/fallido, logout, cambios de credenciales/MFA, denegaciones de autorización, cambios de rol/permisos, accesos a datos `RESTRICTED`, acciones administrativas y errores de validación repetidos.
- **MUST** incluir en cada evento: instante UTC, tipo de evento, actor (id interno), recurso, acción, resultado, origen (IP/servicio) y `traceId`/correlación.
- **MUST NOT** registrar contraseñas, tokens, claves, números de tarjeta ni PII innecesaria (ver `pii-and-data-classification`).
- **MUST** neutralizar la inyección en logs: no escribir saltos de línea ni caracteres de control de entrada externa; preferir logs JSON estructurados.
- **MUST** separar el log de auditoría del log técnico, con acceso de solo escritura para la aplicación y lectura restringida.
- **MUST** hacerlo resistente a manipulación: envío casi en tiempo real a un destino aparte (cuenta de logs distinta; en AWS, preparado para AWS no verificado en real), inmutabilidad/retención y control de integridad. En local solo se reproduce el envío a un colector, no la inmutabilidad real.
- **MUST** definir retención según requisito (a confirmar con fuente legal) y alertar sobre eventos críticos (fuerza bruta, escalada de privilegios).
- **SHOULD** emitir los eventos de auditoría desde la capa de aplicación (dominio), no solo desde el proxy, para capturar la intención.
- **SHOULD** garantizar que el fallo del log de auditoría no pase en silencio para operaciones críticas.

## authn-oidc-oauth2

- **MUST** delegar la autenticación en el IdP (Keycloak, D-cerrada); los servicios no almacenan ni verifican contraseñas.
- **MUST** usar Authorization Code con PKCE para SPA y clientes públicos; **MUST NOT** usar Implicit ni Resource Owner Password.
- **MUST** usar Client Credentials para servicio a servicio, con cliente y secreto propios por servicio (`secrets-management`).
- **MUST** configurar las APIs como OAuth2 Resource Server y validar firma (JWKS del emisor), `iss`, `aud` y `exp`.
- **MUST** registrar redirect URIs exactas en el IdP; sin comodines.
- **MUST NOT** guardar tokens de acceso en `localStorage`; en SPA preferir patrón BFF con cookie de sesión `HttpOnly`/`Secure`/`SameSite`.
- **SHOULD** access tokens de vida corta y refresh tokens con rotación.
- **MUST** implementar logout que cierre sesión en el IdP (RP-initiated logout) además de local.
- **SHOULD** exigir MFA en el IdP para roles administrativos.

## authz-rbac-abac-rebac

- **MUST** denegar por defecto; los permisos se conceden explícitamente.
- **MUST** autorizar en el servidor y en cada petición; ocultar un botón en React no es control de acceso.
- **MUST** comprobar propiedad/tenant del recurso concreto, no solo el rol (evita IDOR/BOLA).
- **MUST** usar RBAC para permisos gruesos (roles por función), ABAC cuando dependa de atributos (tenant, estado, importe) y ReBAC cuando dependa de relaciones (propietario, miembro del equipo).
- **MUST** centralizar la decisión en un componente (`PermissionEvaluator`/servicio de política), no esparcir `if (role...)`.
- **MUST** derivar el tenant del token autenticado, **MUST NOT** aceptarlo de un parámetro o cabecera del cliente.
- **SHOULD** devolver 404 (no 403) cuando revelar la existencia del recurso sea sensible.
- **SHOULD** registrar las denegaciones (`audit-trail-and-security-logging`).
- **MUST NOT** codificar roles en cadenas dispersas; usar constantes o enum.

## cloud-iam-least-privilege

- **MUST NOT** usar `"Action": "*"` ni `"Resource": "*"` en políticas de workload; listar acciones y ARN concretos.
- **MUST NOT** conceder `iam:*`, `sts:AssumeRole` abierto ni `iam:PassRole` sin restringir el rol y el servicio destino (`iam:PassedToService`).
- **MUST** usar un rol por workload y entorno, con credenciales temporales (roles, IRSA); **MUST NOT** crear usuarios IAM con claves de acceso para aplicaciones.
- **MUST** acotar con condiciones cuando aplique (`aws:SourceArn`, `aws:SourceAccount`, `aws:PrincipalOrgID`, `aws:RequestedRegion`).
- **MUST** definir confianza (trust policy) con el principal exacto; en OIDC (CI, EKS) restringir `sub` y `aud`.
- **MUST** exigir permission boundaries o SCP para roles creados por equipos.
- **SHOULD** derivar permisos reales con análisis de acceso (IAM Access Analyzer, política generada a partir de CloudTrail) y revisarlos periódicamente.
- **SHOULD** políticas de recurso que denieguen acceso público y tráfico sin TLS (`aws:SecureTransport`).
- **SHOULD** validar con herramientas estáticas antes de aplicar (Checkov, `terraform validate`, Access Analyzer `validate-policy`).

## container-and-k8s-security

- **MUST** ejecutar como no root (`runAsNonRoot: true`, UID numérico) con `allowPrivilegeEscalation: false`.
- **MUST** descartar todas las capabilities (`drop: ["ALL"]`) y añadir solo las imprescindibles; **MUST NOT** usar `privileged: true`, `hostNetwork`, `hostPID` ni montar `hostPath` ni el socket del runtime.
- **MUST** usar `readOnlyRootFilesystem: true` con `emptyDir` para rutas de escritura, y `seccompProfile: RuntimeDefault`.
- **MUST** definir `resources.requests/limits` en todos los contenedores.
- **MUST** partir de imagen base mínima y mantenida (distroless o equivalente), multi-stage, sin herramientas de build ni shell en runtime; **MUST NOT** usar `latest`; fijar por digest.
- **MUST NOT** incluir secretos en la imagen ni en variables del manifiesto en claro (ver `secrets-management`).
- **MUST** aplicar `NetworkPolicy` con denegación por defecto y reglas explícitas de entrada/salida.
- **MUST** usar una `ServiceAccount` por workload con `automountServiceAccountToken: false` salvo necesidad, y RBAC de mínimo privilegio; **MUST NOT** usar `cluster-admin` para aplicaciones.
- **SHOULD** aplicar Pod Security Admission en modo `restricted` por namespace y Kyverno/OPA para reglas propias.
- **SHOULD** escanear imágenes (Trivy, OSS) en CI y en registro.
- Honestidad: la fábrica valida manifiestos de forma estática; el comportamiento en un clúster EKS real no está verificado.

## crypto-tls-mtls-key-rotation

- **MUST NOT** diseñar primitivas propias; usar bibliotecas contrastadas (JCA con proveedores estándar, Tink) y APIs de alto nivel.
- **MUST** usar AES-GCM (o ChaCha20-Poly1305) con nonce/IV único por mensaje; **MUST NOT** usar ECB, DES/3DES, RC4, MD5 ni SHA-1 para seguridad.
- **MUST** hashear contraseñas con Argon2id, bcrypt o scrypt (`DelegatingPasswordEncoder` de Spring Security); **MUST NOT** usar SHA-256 simple ni sin sal.
- **MUST** usar `SecureRandom` para tokens, IVs y sales.
- **MUST** exigir TLS 1.2 como mínimo (preferir 1.3) en todo tráfico, también interno; verificar certificado y nombre de host, **MUST NOT** deshabilitar la verificación ni usar `TrustAllManager`.
- **MUST** usar mTLS entre servicios cuando la política de zero-trust lo requiera; en malla Istio, `PeerAuthentication` en modo `STRICT` (D-Istio).
- **MUST** cifrar con claves gestionadas (KMS: AWS KMS, preparado para AWS no verificado en real); envelope encryption para datos grandes. En local se sustituye por una clave de prueba: KMS real no se reproduce.
- **MUST** definir rotación para cada clave y certificado (automática donde sea posible), con soporte de versión de clave (`kid`) para descifrar con la anterior durante la transición.
- **SHOULD** emitir certificados de vida corta y automatizar renovación (cert-manager u homólogo, comprobar al fijar la versión).
- **SHOULD** tener plan de agilidad criptográfica (algoritmo y versión almacenados junto al dato).

## dependency-security

- **MUST** ejecutar análisis de composición (SCA) en cada PR y de forma periódica sobre la rama principal: OWASP Dependency-Check (OSS) u OSV-Scanner; Trivy para imágenes. Sin herramientas de pago por defecto (D16).
- **MUST** hacer fallar el build ante vulnerabilidades con severidad `CRITICAL` (y `HIGH` explotables) sin excepción aprobada y con fecha de caducidad.
- **MUST** fijar versiones (sin rangos `LATEST`/`RELEASE`/`^` abiertos en producción) y usar un BOM/`dependencyManagement` común.
- **MUST** usar lockfile (`package-lock.json`) y `npm ci` en CI.
- **MUST** documentar cada excepción (suppression) con CVE, motivo, responsable y fecha de revisión; **MUST NOT** suprimir de forma global.
- **MUST** evaluar alcance real: la vulnerabilidad solo importa si el código vulnerable es alcanzable; registrar la conclusión.
- **SHOULD** minimizar dependencias; eliminar las no usadas (`mvn dependency:analyze`).
- **SHOULD** preferir bibliotecas mantenidas (actividad, releases, múltiples mantenedores) y revisar nuevas dependencias antes de añadirlas.
- **MUST** verificar que el paquete existe y es el correcto antes de instalarlo (typosquatting, nombres inventados por un LLM).
- **SHOULD** usar un repositorio proxy interno (Nexus/Artifactory OSS u otro sin licencia de pago) como único origen.

## deserialization-xxe-ssrf-traversal

- **MUST NOT** usar `ObjectInputStream`/serialización nativa Java con datos externos; usar JSON o Protobuf con esquema.
- **MUST NOT** activar `enableDefaultTyping`/`activateDefaultTyping` de Jackson; si hay polimorfismo, usar `PolymorphicTypeValidator` con allowlist de subtipos.
- **MUST** deshabilitar DTD y entidades externas en todo parser XML (`disallow-doctype-decl`, `XMLConstants.ACCESS_EXTERNAL_DTD` vacío).
- **MUST** validar destinos salientes (SSRF): solo `https`, host en allowlist, resolver DNS y rechazar IPs de loopback, link-local (`169.254.0.0/16`, incluye metadatos de instancia), privadas y reservadas.
- **MUST NOT** seguir redirecciones automáticamente en llamadas con URL aportada por el usuario; revalidar cada salto o deshabilitarlas.
- **MUST** normalizar rutas (`Path.normalize()` + `toRealPath()`) y comprobar `startsWith(baseDir)` antes de abrir ficheros.
- **SHOULD** forzar IMDSv2 y limitar el egress de red de la carga para que SSRF tenga poco alcance (preparado para AWS, no verificado en real; en local no se reproduce IMDS).
- **SHOULD** aplicar `ObjectInputFilter` si la serialización nativa es inevitable en código heredado.

## dos-and-rate-limiting

- **MUST** limitar tasa por identidad (usuario, cliente de API) y por IP como respaldo, con respuesta `429` y `Retry-After`.
- **MUST** límites más estrictos en login, recuperación de contraseña y endpoints que envíen correo o SMS.
- **MUST** paginación obligatoria con tamaño máximo en todo listado; sin "devolver todo".
- **MUST** fijar límites de tamaño de cuerpo, de ficheros y de profundidad/complejidad de consultas (GraphQL).
- **MUST** timeouts explícitos en clientes HTTP, BD y colas (`resilience-*`), con circuit breaker y bulkhead para aislar dependencias.
- **MUST NOT** ejecutar expresiones regulares con backtracking catastrófico sobre entrada del usuario (ReDoS); limitar longitud antes.
- **SHOULD** operaciones costosas asíncronas con cola acotada y rechazo cuando se llena.
- **SHOULD** el limitador compartido entre instancias (estado externo) si hay más de una réplica; un contador en memoria por pod no es un límite global.
- **SHOULD** métricas y alertas de 429, saturación de pools y latencia p99.

## file-upload-security

- **MUST** limitar tamaño de fichero y de petición (`spring.servlet.multipart.max-file-size`, `max-request-size`) y número de partes.
- **MUST** validar el tipo con allowlist de extensiones y comprobar el contenido real (magic bytes, p. ej. Apache Tika), no el `Content-Type` del cliente.
- **MUST NOT** usar `getOriginalFilename()` como ruta; generar un nombre propio (UUID) y guardar el original solo como metadato.
- **MUST** almacenar fuera del directorio servido por el servidor web y, preferiblemente, en almacenamiento de objetos privado.
- **MUST** servir las descargas con `Content-Disposition: attachment`, `X-Content-Type-Options: nosniff` y un `Content-Type` fijado por el servidor.
- **MUST** exigir autenticación y autorización por objeto también en la descarga (evitar IDOR).
- **SHOULD** analizar con antivirus/sandbox antes de marcar el fichero como disponible (estado `PENDING` → `CLEAN`).
- **SHOULD** reprocesar imágenes (re-codificar) para eliminar payloads y metadatos EXIF.
- **SHOULD** en URLs prefirmadas: caducidad corta, tamaño y `Content-Type` condicionados, clave de objeto generada por el servidor.
- **MUST NOT** descomprimir archivos sin límite de tamaño total, de entradas y de profundidad (zip bomb) ni sin validar las rutas internas (zip slip).

## injection-families

- **MUST** usar consultas parametrizadas (`PreparedStatement`, parámetros nombrados JPA, Spring Data derivadas) en todo acceso SQL.
- **MUST NOT** concatenar ni formatear (`+`, `String.format`, text blocks interpolados) datos externos dentro de SQL/JPQL/HQL.
- **MUST** validar con lista cerrada (allowlist) los identificadores dinámicos que no se pueden parametrizar (columna de `ORDER BY`, nombre de tabla).
- **MUST NOT** invocar `Runtime.exec`/`ProcessBuilder` con una cadena de shell; si es inevitable, pasar argumentos como lista, sin `sh -c`, con ejecutable fijo.
- **MUST NOT** evaluar entrada externa con `SpelExpressionParser`, motores de plantillas o `ScriptEngine`; usar `SimpleEvaluationContext` si hace falta SpEL.
- **MUST** construir filtros NoSQL con la API tipada del driver (`Filters.eq`), nunca parseando JSON del cliente como filtro.
- **MUST** escapar filtros y DN de LDAP con la API del framework (`LdapEncoder`/filtros de Spring LDAP) y no concatenarlos.
- **SHOULD** ejecutar la aplicación con un usuario de BD de mínimo privilegio, de modo que una inyección tenga radio de daño limitado.
- **SHOULD** devolver errores genéricos al cliente; el detalle SQL va al log.

## input-validation-output-encoding

- **MUST** validar en el servidor (sintaxis y semántica); la validación del cliente React es solo UX.
- **MUST** preferir listas permitidas (formato, longitud, rango, enum) frente a listas de bloqueo.
- **MUST** usar Bean Validation (`@Valid`, `@NotNull`, `@Size`, `@Pattern`) en DTOs de entrada y rechazar con 400 sin eco del valor.
- **MUST** limitar longitud de strings, tamaño de colecciones y profundidad de JSON.
- **MUST** normalizar (Unicode, trim) antes de validar y no re-decodificar tras validar.
- **MUST** codificar la salida según el contexto (HTML, atributo, JS, URL, CSS); usar el escapado por defecto del motor de plantillas.
- **MUST NOT** usar `dangerouslySetInnerHTML` ni `th:utext` con datos no confiables; si es inevitable, sanear con una librería mantenida y una política restrictiva.
- **MUST NOT** construir HTML por concatenación de strings.
- **SHOULD** usar tipos de dominio (`Email`, `OrderId`) que se validan al construirse.

## jwt-and-sessions

- **MUST** verificar firma con las claves públicas del emisor (JWKS); **MUST NOT** aceptar `alg: none` ni permitir que el token elija el algoritmo.
- **MUST** fijar la lista de algoritmos aceptados (p. ej. RS256/ES256) en el decoder.
- **MUST** validar `iss`, `aud`, `exp`, `nbf`; tolerancia de reloj pequeña y explícita.
- **MUST NOT** poner datos sensibles en el payload: un JWT firmado está codificado, no cifrado.
- **MUST** access tokens de vida corta (minutos); refresh tokens con rotación y detección de reutilización.
- **MUST** cookies de sesión con `HttpOnly`, `Secure` y `SameSite` (Lax o Strict), prefijo `__Host-` si es posible.
- **MUST** regenerar el identificador de sesión tras login y destruir la sesión en logout.
- **SHOULD** definir estrategia de revocación (lista de `jti` denegados con TTL, o introspección) para tokens de alto riesgo.
- **MUST NOT** guardar tokens en `localStorage`/`sessionStorage`.
- **MUST NOT** loguear tokens completos.

## llm-security

- **MUST** tratar toda salida del modelo y todo contenido recuperado (web, documentos, correos, resultados de tools) como **entrada no confiable**: es dato, nunca instrucciones con autoridad.
- **MUST NOT** ejecutar la salida del LLM en un intérprete (SQL, shell, `eval`, plantillas) ni renderizarla como HTML sin codificación; validarla contra esquema estricto (JSON Schema) antes de usarla.
- **MUST** aplicar mínimo privilegio a las herramientas del agente: allowlist de tools, permisos acotados por usuario (la autorización se evalúa con la identidad del usuario, no la del agente), credenciales de corta vida.
- **MUST** exigir confirmación humana para acciones irreversibles, de coste o con efectos externos (pagos, borrados, envíos).
- **MUST** separar privilegios: un agente que lee contenido no confiable no debe tener a la vez acceso a datos sensibles y capacidad de exfiltrar (evitar la combinación datos privados + contenido no confiable + canal de salida).
- **MUST NOT** enviar a un proveedor de modelo PII o secretos sin base y contrato aprobados (ver `pii-and-data-classification`); minimizar y enmascarar.
- **MUST** aplicar control de acceso en la recuperación RAG (filtrar por permisos del usuario antes de construir el contexto).
- **SHOULD** limitar longitud, tasa y coste por usuario (ver `dos-and-rate-limiting`) y fijar un máximo de pasos del agente.
- **SHOULD** registrar prompts, tool calls y decisiones para auditoría, sin PII (ver `audit-trail-and-security-logging`).
- **SHOULD** probar con casos adversarios (inyección directa e indirecta) en una batería de evaluación; no hay defensa perfecta de prompt, la contención es arquitectónica.

## method-and-endpoint-security

- **MUST** terminar la cadena con `anyRequest().authenticated()` (o `denyAll()`); la lista de `permitAll` es corta, explícita y revisada.
- **MUST** habilitar method security (`@EnableMethodSecurity`) y proteger la capa de servicio, no solo los controladores.
- **MUST** ordenar matchers de lo específico a lo general.
- **MUST** exponer Actuator solo con `health` y `info` sin detalles; el resto detrás de rol y red de gestión.
- **MUST NOT** desactivar la seguridad con perfiles (`@Profile("dev")` con `permitAll`) sin que el arranque falle si el perfil llega a un entorno compartido.
- **MUST** devolver errores sin stack traces ni detalles internos (`server.error.include-stacktrace=never`, comprobar propiedad).
- **SHOULD** una cadena por tipo de cliente (API stateless vs. web con sesión).
- **SHOULD** probar la seguridad con `spring-security-test`, incluyendo caso anónimo.
- **MUST NOT** depender de ocultar rutas ("security by obscurity").

## owasp-top10-and-api-top10

- **MUST** tratar la autorización a nivel de objeto (BOLA/IDOR) como riesgo n.º 1 de API: todo acceso por id valida propiedad o pertenencia al tenant (`authz-rbac-abac-rebac`).
- **MUST** denegar por defecto: ningún endpoint nuevo queda público salvo lista explícita.
- **MUST** exponer DTOs de respuesta explícitos; nunca serializar entidades JPA (exposición excesiva de propiedades).
- **MUST** aceptar solo los campos esperados en entrada (sin asignación masiva de campos como `role` o `tenantId`).
- **MUST** limitar tamaño, frecuencia y paginación (`dos-and-rate-limiting`).
- **MUST** mantener inventario de APIs y versiones expuestas; desactivar las obsoletas.
- **MUST** validar toda URL aportada por el usuario antes de consumirla (`deserialization-xxe-ssrf-traversal`).
- **SHOULD** revisar la lista vigente anualmente: las categorías cambian entre ediciones (comprobar ediciones actuales de ambos Top 10).

## pii-and-data-classification

- **MUST** clasificar cada dato en un nivel (p. ej. `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`) y registrar la clasificación en el modelo (anotación, esquema o catálogo de datos).
- **MUST** minimizar: no recoger, devolver ni copiar a otros servicios más PII de la necesaria.
- **MUST NOT** escribir PII ni secretos en logs, trazas, métricas, mensajes de error ni URLs (query strings); enmascarar o tokenizar.
- **MUST** cifrar en tránsito y en reposo los datos `CONFIDENTIAL`/`RESTRICTED`; cifrado a nivel de campo para los más sensibles.
- **MUST NOT** usar datos reales de producción en desarrollo, tests ni prompts a LLM; usar sintéticos o anonimizados.
- **MUST** definir retención y borrado por categoría, con procedimiento comprobable (incluidas copias de seguridad y réplicas).
- **MUST** limitar el acceso por necesidad y registrar accesos a datos `RESTRICTED` (ver `audit-trail-and-security-logging`).
- **SHOULD** pseudonimizar en analítica y separar la tabla de identificadores del resto.
- **SHOULD** respetar residencia de datos por región; en AWS depende de la configuración de la cuenta (preparado para AWS, no verificado en real).
- **MUST** no duplicar el dato personal entre Postgres y un almacén NoSQL como doble escritura (regla 4.5); un único sistema de registro.

## secrets-management

- **MUST NOT** commitear secretos reales (código, `application.yml`, `.env`, Terraform, tfstate, imágenes Docker, logs).
- **MUST** inyectar secretos en runtime desde un gestor: AWS Secrets Manager o SSM Parameter Store (preparado para AWS, no verificado en real) y Vault OSS u OpenBao u otro gestor sin licencia de pago como equivalente local (D16). No se reproduce en local la integración IAM/KMS de AWS.
- **MUST** usar credenciales efímeras cuando exista la opción (roles IAM, IRSA, credenciales dinámicas de BD) antes que claves estáticas.
- **MUST** poder rotar cada secreto sin redespliegue de código y con plan documentado (frecuencia, responsable, procedimiento).
- **MUST** tratar como comprometido y rotar de inmediato cualquier secreto que haya llegado a un commit, log o chat; borrar el historial no basta.
- **MUST** ejecutar escaneo de secretos en pre-commit y en CI.
- **MUST NOT** pasar secretos por argumentos de línea de comandos, variables de build (`ARG`) ni imprimirlos en logs/trazas.
- **SHOULD** preferir ficheros montados o API del gestor frente a variables de entorno (se filtran en volcados y `/proc`).
- **SHOULD** un secreto por servicio y entorno, con permisos de lectura mínimos.
- **MUST** usar en ejemplos y tests valores falsos con `example` o `changeme`.

## secure-sdlc-nist-ssdf

- **MUST** mapear cada fase (requisitos, diseño, implementación, verificación, entrega, operación) a los cuatro grupos SSDF: PO (preparar la organización), PS (proteger el software), PW (producir software bien asegurado), RV (responder a vulnerabilidades).
- **MUST** producir una evidencia verificable por práctica aplicada (fichero, informe de CI, ADR); sin evidencia la práctica cuenta como no cumplida.
- **MUST** exigir modelo de amenazas (`threat-modeling-stride`) antes de la fase de implementación en servicios que expongan API o traten datos personales.
- **MUST** ejecutar en CI análisis estático, de dependencias y de secretos (`security-testing-sast-dast`, `dependency-security`, `secrets-management`).
- **MUST** definir un canal de reporte de vulnerabilidades y un SLA (`vulnerability-sla-and-incident-response`).
- **SHOULD** registrar las excepciones de seguridad como ADR con caducidad y dueño.
- **MUST NOT** declarar "conforme con SSDF" o "certificado"; usar "alineado con SSDF, evidencias en `docs/security/`".

## security-headers-cors-csrf

- **MUST** enviar `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` y una `Content-Security-Policy` restrictiva en el frontend.
- **MUST** CSP sin `unsafe-inline`/`unsafe-eval` en scripts; usar nonces o hashes; empezar en `Content-Security-Policy-Report-Only` si hay deuda.
- **MUST** definir `frame-ancestors` (o `X-Frame-Options`) para evitar clickjacking.
- **MUST** CORS con lista explícita de orígenes; **MUST NOT** `*` con credenciales ni reflejar el `Origin` recibido sin validarlo.
- **MUST** mantener CSRF activo en apps con sesión por cookie; usar token sincronizado o doble cookie más `SameSite`.
- **MAY** desactivar CSRF solo en APIs stateless con token Bearer en cabecera `Authorization`, dejándolo documentado.
- **MUST** respuestas con datos sensibles con `Cache-Control: no-store`.
- **SHOULD** terminar las cabeceras en un único punto (app o gateway) para no duplicarlas ni contradecirlas.
- **SHOULD** verificar con un escáner de cabeceras en CI.

## security-testing-sast-dast

- **MUST** SAST en cada pull request (Semgrep OSS u otro de licencia abierta, D16) con reglas de `policies/semgrep/` más un conjunto base mantenido; salida SARIF.
- **MUST** escaneo de secretos en commits y en CI (`secrets-management`).
- **MUST** análisis de dependencias en CI (`dependency-security`).
- **MUST** DAST (p. ej. OWASP ZAP en modo baseline) contra un entorno efímero o local, nunca contra sistemas ajenos ni sin autorización.
- **MUST** tests de seguridad unitarios/integración para controles propios: acceso cruzado, token inválido, validación, límites.
- **MUST** definir umbral de bloqueo (p. ej. severidad alta/crítica bloquea merge) y proceso de excepción con caducidad.
- **MUST** triaje de falsos positivos con justificación versionada (fichero de supresiones con motivo y fecha), no desactivar la regla globalmente.
- **SHOULD** ejecutar SAST rápido en PR y DAST completo de forma nocturna o por release.
- **MUST NOT** tratar "0 hallazgos" como "seguro": indica solo que las reglas no detectaron nada.

## supply-chain

- **MUST** generar un SBOM por artefacto en cada release (CycloneDX o SPDX) y conservarlo junto al artefacto.
- **MUST** construir en CI desde el commit etiquetado en un entorno efímero y sin acceso de escritura manual; **MUST NOT** publicar artefactos desde máquinas de desarrollo.
- **MUST** firmar las imágenes y artefactos con cosign (Sigstore); preferir firma sin clave (keyless/OIDC) o claves en KMS; **MUST NOT** guardar claves de firma en el repositorio.
- **MUST** emitir atestaciones de procedencia (SLSA provenance) y SBOM como atestación asociada a la imagen.
- **MUST** verificar firma y procedencia antes de admitir un artefacto en el clúster (admission control: Kyverno `verifyImages`); referenciar imágenes por digest `@sha256:`, no por tag mutable.
- **MUST** fijar acciones de CI por SHA de commit y limitar permisos del token de CI (`permissions:` mínimos).
- **SHOULD** apuntar a un nivel SLSA objetivo explícito (p. ej. nivel de build 2 → 3) y declarar el que realmente se cumple; **MUST NOT** afirmar un nivel sin evidencia.
- **SHOULD** buscar builds reproducibles (ver `reproducible-builds`).
- **SHOULD** usar registro propio (Harbor, sin licencia de pago) con política de solo imágenes firmadas.
- Honestidad: la fábrica no despliega ni firma en real; todo esto queda como "validado estáticamente".

## threat-modeling-stride

- **MUST** partir de un diagrama de flujo de datos (DFD) con actores, procesos, almacenes, flujos y fronteras de confianza.
- **MUST** evaluar cada elemento y flujo que cruce una frontera con las seis categorías: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.
- **MUST** registrar por amenaza: id, descripción, impacto, probabilidad, mitigación, dueño y estado.
- **MUST** convertir cada mitigación aceptada en una historia o tarea con prueba asociada.
- **MUST** documentar los riesgos aceptados con firma del dueño del producto y fecha de revisión.
- **SHOULD** versionar el modelo junto al código (`docs/security/threat-model-<servicio>.md`) y revisarlo cuando cambie el DFD.
- **SHOULD** incluir abuso de negocio (cupones, reintentos, enumeración), no solo técnica.
- **MUST NOT** limitar el modelo a una checklist genérica sin DFD.

## vulnerability-sla-and-incident-response

- **MUST** priorizar por severidad ajustada al contexto (CVSS base + explotabilidad conocida + exposición + criticidad del activo), no solo por el CVSS bruto.
- **MUST** fijar un SLA de corrección por severidad, con dueño y fecha límite en cada hallazgo. Punto de partida propuesto (a validar por el responsable): crítica explotable 48 h, alta 7 días, media 30 días, baja 90 días.
- **MUST** pedir una excepción formal para incumplir el SLA: riesgo, mitigación compensatoria, aprobador y caducidad.
- **MUST** mantener un inventario actualizado (SBOM) para responder rápido a una vulnerabilidad nueva.
- **MUST** tener un plan de respuesta a incidentes con roles (comandante, comunicaciones, técnico), canal de crisis y árbol de escalado.
- **MUST** seguir las fases: detección y triaje, contención, erradicación, recuperación, comunicación y post-mortem sin culpables.
- **MUST** preservar evidencias antes de limpiar (logs, copias de disco/memoria si procede) y registrar la línea de tiempo.
- **MUST** rotar credenciales potencialmente expuestas (ver `secrets-management`) durante la contención.
- **SHOULD** ensayar el plan con simulacros (game days) al menos una vez al año.
- **SHOULD** publicar un canal de divulgación responsable (`security.txt`, RFC 9116) y responder a los reportes en plazo.
- **SHOULD** cerrar cada incidente con acciones correctivas rastreadas hasta su cierre y una regla/test que lo detecte la próxima vez.

## zero-trust

- **MUST** autenticar y autorizar cada petición, también entre servicios internos; estar dentro de la red no concede permisos.
- **MUST** identidad por carga de trabajo (cuenta de servicio de Kubernetes, identidad SPIFFE de Istio), no por IP ni por secreto compartido.
- **MUST** mTLS entre servicios en la malla (Istio, decisión cerrada) en modo `STRICT` en namespaces de aplicación.
- **MUST** NetworkPolicy/AuthorizationPolicy con denegar por defecto y reglas explícitas origen -> destino.
- **MUST** propagar la identidad del usuario final (token) y validarla en cada servicio; **MUST NOT** confiar en una cabecera `X-User-Id` interna sin firma.
- **MUST** mínimo privilegio en acceso a datos: credenciales por servicio, solo las tablas/colas necesarias (`cloud-iam-least-privilege`).
- **SHOULD** segmentar por sensibilidad (datos personales en segmentos aparte) y registrar accesos (`audit-trail-and-security-logging`).
- **SHOULD** acceso de operadores con identidad individual, MFA y caducidad, sin credenciales compartidas.
