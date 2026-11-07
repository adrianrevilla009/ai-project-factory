# Estándares · 09-build-supply-chain

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## bom-management

- **MUST** importar los BOM por `<scope>import</scope>` con `<type>pom</type>` dentro de `dependencyManagement`; orden: BOM corporativo primero, resto después (el primero que declara gana).
- **MUST** que los módulos declaren dependencias SIN `<version>` cuando el BOM la gestiona.
- **MUST** que el BOM corporativo importe `spring-boot-dependencies` y fije versiones de librerías aprobadas (`catalog/approved-libraries.yaml`); las versiones concretas son TODO-VERIFY hasta confirmarlas en fuente oficial.
- **MUST** documentar cada override de versión con comentario, motivo (CVE, bug), ticket y fecha de retirada.
- **SHOULD** versionar el BOM con semver y publicarlo como artefacto propio (`com.example:platform-bom`).
- **SHOULD** que el BOM sea solo `dependencyManagement`: sin `<dependencies>`.
- **MUST NOT** redefinir propiedades `*.version` de Spring Boot sin pasar por el BOM.
- **MUST NOT** usar licencias de pago ni librerías fuera de `approved-libraries.yaml` sin ADR.

## build-caching-and-speed

- **MUST** medir antes de optimizar: registrar tiempo total y por fase (resolución, compilación, tests, empaquetado).
- **MUST** cachear el repositorio local de Maven (`~/.m2/repository`) en CI con clave derivada de los `pom.xml` (hash), nunca con clave fija.
- **MUST NOT** cachear `target/` entre ramas ni reutilizar resultados sin que la clave incluya código y versión de JDK.
- **SHOULD** usar `./mvnw -T 1C` (módulos en paralelo) solo si los módulos y tests son thread-safe; empezar por `-T 1`.
- **SHOULD** usar `-B` (batch) y `--no-transfer-progress` en CI para logs limpios.
- **SHOULD** separar tests rápidos (unit, `surefire`) de lentos (integración, `failsafe`) en etapas distintas.
- **MAY** evaluar la extensión Maven Build Cache; TODO-VERIFY estado, versión y compatibilidad con los plugins usados.
- **MUST** ordenar el Dockerfile para cachear capas: dependencias antes del código (ver `container-images`).
- **MUST NOT** desactivar tests, enforcer o análisis (`-DskipTests`, `-Denforcer.skip`) para ir más rápido en la rama principal.

## container-images

- **MUST** usar build multi-stage: una etapa de build (JDK) y una etapa final solo con JRE y el artefacto.
- **MUST** fijar la imagen base por versión y por digest (`@sha256:`) en la etapa final; actualizar el digest mediante Renovate (`renovate-dependabot-policy`).
- **MUST NOT** usar la etiqueta `latest` ni imágenes sin versión.
- **MUST** ejecutar como usuario no root (`USER` numérico) y sin privilegios añadidos.
- **MUST NOT** incluir secretos, `.git`, claves ni `settings.xml` con credenciales en la imagen ni en capas intermedias; usar `.dockerignore`.
- **MUST** usar una base de distribución OpenJDK libre y soportada (`jdk-distribution-and-upgrade-cadence`); sin runtimes de pago por defecto (D16).
- **SHOULD** usar el JAR en capas de Spring Boot (layertools) para cachear dependencias frente a código.
- **SHOULD** declarar `HEALTHCHECK` solo si el orquestador no lo cubre; en Kubernetes se usan probes.
- **MUST** escanear la imagen y generar su SBOM (`sbom-generation`) en CI; fallar con vulnerabilidades críticas según `vulnerability-sla-and-incident-response`.
- **SHOULD** firmar la imagen y verificar la firma en admisión (Kyverno, pendiente en `policies/kyverno/`). Preparado para AWS, no verificado en real: publicar en ECR queda fuera de la fábrica (D4).

## dependency-hygiene

- **MUST** justificar toda dependencia nueva en el PR (qué problema resuelve y alternativa JDK/Spring considerada); debe estar en `catalog/approved-libraries.yaml` o llevar ADR.
- **MUST** declarar explícitamente lo que el código usa (no depender de transitivas): `mvn dependency:analyze` sin "used undeclared".
- **MUST** eliminar las "unused declared" salvo excepción documentada (`ignoredUnusedDeclaredDependencies`).
- **MUST** usar `scope` correcto: `test`, `provided`, `runtime`; **MUST NOT** dejar librerías de test en `compile`.
- **MUST** excluir transitivas problemáticas con `<exclusions>` comentadas, no con versiones forzadas ad hoc.
- **MUST** commitear el lockfile de frontend (`package-lock.json` o `pnpm-lock.yaml`) e instalar en CI con `npm ci` / `pnpm install --frozen-lockfile`.
- **SHOULD** preferir `starter` de Spring Boot sobre listas manuales de artefactos.
- **SHOULD** revisar el árbol (`dependency:tree`) cuando una dependencia añade más de ~10 transitivas.
- **MUST NOT** añadir librerías abandonadas (sin release en >2 años, TODO-VERIFY umbral) sin ADR.

## enforcer-rules

- **MUST** ejecutar `maven-enforcer-plugin` en fase `validate` desde el parent, con `fail=true`.
- **MUST** incluir: `requireMavenVersion`, `requireJavaVersion`, `requirePluginVersions`, `banDuplicatePomDependencyVersions`, `dependencyConvergence`.
- **MUST** derivar `bannedDependencies` de `catalog/forbidden-libraries.yaml` (fuente de verdad); incluir `org.projectlombok:lombok` (D27, skill `no-lombok`), `log4j:log4j`, `commons-collections:commons-collections`, `joda-time:joda-time`.
- **MUST** usar `searchTransitive=true` para que una dependencia transitiva prohibida también falle.
- **MUST** añadir `requireReleaseDeps` y `requireReleaseVersion` en el perfil `release` (ver `versioning-semver-snapshots`).
- **SHOULD** en módulos `*-domain` banear `org.springframework:*` y `jakarta.persistence:*`.
- **SHOULD** dar un `<message>` accionable en cada regla que apunte al skill.
- **MUST NOT** desactivar el enforcer con `-Denforcer.skip=true` en CI.
- **MUST NOT** añadir excepciones sin ADR y fecha de caducidad.

## jdk-distribution-and-upgrade-cadence

- **MUST** usar una versión LTS de JDK como objetivo; usar versiones no LTS solo en experimentos, nunca en producción.
- **MUST** elegir una distribución OpenJDK de licencia libre con actualizaciones de seguridad (p. ej. Eclipse Temurin); sin licencias de pago por defecto (D16). Cambiar de distribución requiere ADR.
- **MUST** usar la misma distribución y versión mayor en desarrollo, CI e imagen de runtime (`maven-wrapper-and-toolchains`, `container-images`).
- **MUST** documentar en `docs/` del proyecto el JDK objetivo, la fecha de fin de soporte y la fecha prevista de migración. Fechas: TODO-VERIFY en la hoja de ruta oficial de la distribución.
- **MUST** aplicar parches de seguridad (actualizaciones trimestrales del JDK) mediante PR automatizado de Renovate y pasar toda la suite.
- **SHOULD** planificar la subida al siguiente LTS cuando la versión actual entre en el último año de soporte, no cuando termine.
- **MUST** comprobar compatibilidad antes de subir: versión mínima de Java de Spring Boot, plugins Maven, agente de OpenTelemetry y librerías con bytecode manipulation (TODO-VERIFY en cada documentación).
- **SHOULD** compilar con `release` al nivel del JDK objetivo y ejecutar CI en la matriz [actual, siguiente LTS] como aviso temprano.
- **MUST NOT** activar `--enable-preview` en código de producción.

## license-compliance

- **MUST** mantener una lista de licencias permitidas, a revisar y prohibidas en un único fichero versionado del proyecto (`legal/license-policy.yaml`).
- **MUST** permitir por defecto solo licencias permisivas: Apache-2.0, MIT, BSD-2/3-Clause, ISC, EPL-2.0, MPL-2.0 (a nivel de fichero, sin modificar).
- **MUST** tratar como "revisión humana" LGPL, EPL con exclusión secundaria y licencias duales.
- **MUST NOT** introducir AGPL, SSPL, BUSL, Commons Clause ni licencias de pago por defecto (D16); si se necesita una, abrir ADR.
- **MUST** generar el informe de licencias en cada build de CI y fallar si aparece una licencia prohibida o desconocida.
- **MUST** registrar toda excepción con dependencia, versión, motivo, aprobador y fecha de caducidad.
- **SHOULD** cruzar el informe con el SBOM (`sbom-generation`) para cubrir dependencias transitivas.
- **MUST NOT** copiar código de repositorios externos al proyecto sin verificar su licencia.

## maven-multimodule-layout

- **MUST** separar el `pom.xml` raíz en dos roles claros: parent (configuración heredada, ver `parent-pom`) y aggregator (`<modules>`). Pueden coincidir en el raíz, pero sin lógica de negocio.
- **MUST** nombrar módulos por responsabilidad, no por capa técnica genérica: `orders-domain`, `orders-application`, `orders-adapter-rest`, `orders-adapter-jpa`, `orders-boot`.
- **MUST** que `*-domain` no dependa de Spring, JPA ni de adaptadores; solo del JDK y librerías puras.
- **MUST** que las dependencias entre módulos formen un DAG dirigido hacia el dominio (adapter -> application -> domain). Cero ciclos.
- **MUST** que solo el módulo `*-boot` aplique `spring-boot-maven-plugin` y contenga la clase `@SpringBootApplication`.
- **SHOULD** declarar las versiones de módulos internos con `${project.version}` en `dependencyManagement` del parent, nunca literales repetidos.
- **SHOULD** usar un módulo `*-bom` o `dependencyManagement` propio si hay más de 3 módulos publicables (ver `bom-management`).
- **MUST NOT** crear módulos `common`/`utils` cajón de sastre.
- **MUST NOT** usar `<scope>system</scope>` ni `systemPath`.

## maven-wrapper-and-toolchains

- **MUST** versionar `mvnw`, `mvnw.cmd` y `.mvn/wrapper/maven-wrapper.properties` en el repositorio.
- **MUST** invocar siempre `./mvnw` (local, CI, Docker); **MUST NOT** depender de un `mvn` instalado en la máquina.
- **MUST** fijar la versión de Maven en el wrapper y exigirla con `maven-enforcer-plugin` (`requireMavenVersion`, ver `enforcer-rules`).
- **MUST** declarar el JDK de compilación con toolchains o con `maven.compiler.release`, no con lo que haya en el `PATH`.
- **SHOULD** usar `maven-toolchains-plugin` y un `toolchains.xml` generado en CI (no versionar rutas absolutas personales).
- **MUST** usar `release` (no solo `source`/`target`) para que la API compilada coincida con el JDK objetivo.
- **SHOULD** fijar la versión del propio plugin del wrapper al actualizarlo y revisar el diff de `maven-wrapper.properties` (la URL de distribución es superficie de ataque).
- **MUST NOT** apuntar `distributionUrl` a repositorios no corporativos sin verificar checksum.

## parent-pom

- **MUST** fijar en propiedades: `java.version` (o `maven.compiler.release`), `project.build.sourceEncoding=UTF-8` y `project.build.outputTimestamp` (ver `reproducible-builds`).
- **MUST** declarar versiones de plugins en `<pluginManagement>`; ningún plugin sin versión explícita.
- **MUST** usar `maven.compiler.release` en lugar de `source`/`target` para compilar contra la API correcta del JDK.
- **MUST** aplicar el enforcer (`maven-enforcer-plugin`) desde el parent con las reglas de `enforcer-rules`.
- **SHOULD** heredar de `spring-boot-starter-parent` solo si el parent corporativo no puede importar el BOM de Spring Boot; si ya hay parent corporativo, importar `spring-boot-dependencies` por scope `import`.
- **SHOULD** mantener perfiles mínimos (`ci`, `release`); la lógica específica de entorno va fuera del POM.
- **MUST NOT** declarar `<repositories>` ni `<pluginRepositories>` en el POM: la resolución va por `settings.xml`/mirror corporativo.
- **MUST NOT** meter dependencias reales en `<dependencies>` del parent salvo las realmente universales (p. ej. test).
- **MUST NOT** usar rangos de versión (`[1.0,)`), `LATEST` ni `RELEASE`.

## release-automation

- **MUST** derivar el tipo de incremento (major/minor/patch) de Conventional Commits y de `versioning-semver-snapshots`, no de decisión manual ad hoc.
- **MUST** hacer la release desde CI sobre la rama principal limpia y con la verificación completa en verde; **MUST NOT** liberar desde una máquina local.
- **MUST** generar changelog automático a partir de los commits y crear un tag anotado `vX.Y.Z`.
- **MUST** publicar en cada release: artefactos, SBOM (`sbom-generation`), informe de licencias y, si aplica, imagen con digest (`container-images`).
- **SHOULD** usar versiones CI-friendly (`${revision}` con `flatten-maven-plugin`) o `maven-release-plugin`; elegir una y documentarla en un ADR. Detalles TODO-VERIFY.
- **MUST** hacer la release idempotente: re-ejecutarla sobre el mismo tag no debe producir artefactos distintos (`reproducible-builds`).
- **MUST NOT** reescribir ni borrar un tag publicado; corregir con una nueva versión patch.
- **MUST** exigir aprobación humana antes de promocionar a entornos productivos (gate); el agente MUST NOT crear ni editar `approvals/*.json`.
- **SHOULD** limitar secretos de publicación a un entorno protegido de CI con permisos mínimos.

## renovate-dependabot-policy

- **MUST** tener un bot de actualización activo: Dependabot (integrado en GitHub, sin coste) o Renovate (OSS autoalojable; TODO-VERIFY licencia y opción gratuita vigente antes de elegirlo).
- **MUST** cubrir ecosistemas: `maven`, `npm`, `docker`/imágenes base, `github-actions` y Terraform si existe.
- **MUST** agrupar en un PR: dependencias de Spring Boot, de test y minor/patch de frontend; **MUST NOT** abrir un PR por cada patch.
- **MUST** exigir CI verde y revisión humana para `major`; el automerge solo para `patch` de test/dev y con CI verde.
- **MUST** fijar cadencia (semanal) y límite de PRs abiertos (p. ej. 5).
- **MUST** que las actualizaciones del BOM corporativo se propongan sobre el BOM, no sobre versiones literales en módulos (ver `bom-management`).
- **SHOULD** fijar imágenes Docker por digest además de por tag (ver `container-images`) y dejar que el bot lo actualice.
- **MUST NOT** automergear dependencias de runtime ni plugins de build.
- **MUST NOT** guardar tokens del bot en el repo.

## reproducible-builds

- **MUST** definir `project.build.outputTimestamp` en el parent (valor fijo ISO-8601 o derivado del commit en release) para que los plugins de empaquetado normalicen fechas.
- **MUST** fijar versiones de todos los plugins y del propio Maven (wrapper, ver `maven-wrapper-and-toolchains`).
- **MUST** usar `project.build.sourceEncoding=UTF-8` y `maven.compiler.release` fijo.
- **MUST NOT** incrustar fecha/hora actual, hostname o usuario en el artefacto (`${maven.build.timestamp}` en recursos filtrados, `git.build.time` sin normalizar).
- **MUST NOT** usar rangos de versión, `LATEST` ni dependencias SNAPSHOT en release (ver `versioning-semver-snapshots`).
- **SHOULD** verificar la reproducibilidad en CI construyendo dos veces y comparando (`maven-artifact-plugin`, objetivo `compare`; TODO-VERIFY disponibilidad en la versión elegida).
- **SHOULD** que las imágenes usen base fijada por digest y capas ordenadas; comprobar con `SOURCE_DATE_EPOCH`/opciones del builder (ver `container-images`, TODO-VERIFY según herramienta).
- **MUST** conservar la salida de la verificación como evidencia, sin afirmar nada sobre despliegues reales.

## sbom-generation

- **MUST** generar un SBOM en formato CycloneDX (JSON) por cada release, a partir del grafo de dependencias real resuelto.
- **MUST** usar el plugin `org.cyclonedx:cyclonedx-maven-plugin` con versión fijada en `pluginManagement` del parent (`parent-pom`); versión exacta TODO-VERIFY.
- **MUST** en multimódulo producir un SBOM agregado (goal `makeAggregateBom`) y no solo uno por módulo.
- **MUST** generar también el SBOM de la imagen final (`container-images`), no solo del JAR.
- **MUST** adjuntar el SBOM a la release como artefacto y conservarlo con la misma retención que el binario.
- **MUST NOT** editar a mano un SBOM; se regenera siempre desde el build.
- **SHOULD** alimentar el SBOM a la herramienta de análisis de vulnerabilidades y a `license-compliance`.
- **SHOULD** incluir el `serialNumber`/versión de build para trazar qué SBOM corresponde a qué release.

## versioning-semver-snapshots

- **MUST** seguir SemVer `MAJOR.MINOR.PATCH`: MAJOR rompe compatibilidad, MINOR añade compatible, PATCH corrige.
- **MUST** que las versiones release sean inmutables: una versión publicada nunca se re-sube ni se sobrescribe; se corrige con una nueva.
- **MUST** que `-SNAPSHOT` exista solo en ramas de desarrollo; **MUST NOT** desplegar ni referenciar SNAPSHOT en un release ni en una imagen de producción.
- **MUST NOT** depender de un SNAPSHOT de terceros en `main`.
- **SHOULD** usar CI-friendly versions (`${revision}`) con `flatten-maven-plugin` para que el POM publicado lleve la versión resuelta (TODO-VERIFY compatibilidad con la versión de Maven elegida).
- **SHOULD** derivar la versión de un tag git `vX.Y.Z` en el pipeline de release (ver `release-automation`).
- **SHOULD** que todos los módulos de un reactor compartan la misma versión.
- **MUST NOT** usar `versions:set` manual con commits "bump version" a mano si hay automatización.
