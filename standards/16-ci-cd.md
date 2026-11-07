# Estándares · 16-ci-cd

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## alternatives

- **MUST** mantener las reglas de `pipeline-architecture` y los gates, independientemente de la herramienta.
- **MUST** registrar la excepción a D20 en un ADR del proyecto con motivo y coste de mantener guías duplicadas.
- **MUST** conservar los tres principios de D20: pipelines reutilizables, credenciales cortas por OIDC y dependencias fijadas inmutablemente.
- **SHOULD** preferir GitLab CI con `include:` de plantillas versionadas por SHA/tag protegido y `id_tokens` para OIDC (TODO-VERIFY sintaxis).
- **SHOULD** si se usa Jenkins: Jenkinsfile declarativo, shared libraries versionadas, agentes efímeros (pods) y plugins mínimos fijados.
- **MUST NOT** guardar claves de nube de larga vida en el servidor de CI ni ejecutar builds en el controlador de Jenkins.
- **MUST NOT** exigir licencias de pago por defecto (D16).

## contract-gate

- **MUST** publicar los pacts del consumidor en el Pact Broker en cada build, con la versión = SHA del commit y la rama.
- **MUST** que el proveedor verifique y publique resultados de verificación en CI.
- **MUST** ejecutar `pact-broker can-i-deploy` antes de cada promoción a un entorno; código de salida distinto de 0 aborta el despliegue.
- **MUST** ejecutar `pact-broker record-deployment` tras un despliegue correcto para que el Broker conozca qué versión está en cada entorno.
- **SHOULD** usar webhooks del Broker para disparar la verificación del proveedor cuando cambia un contrato.
- **MUST NOT** usar `--ignore` ni forzar el resultado para saltarse el gate sin PR de excepción.
- **MUST NOT** depender de un Broker de pago por defecto (D16/D19): Pact Broker OSS autoalojado.

## database-migration-step

- **MUST** ejecutar la migración como paso explícito y previo al despliegue de la aplicación (job o Kubernetes Job), no al arrancar N réplicas a la vez.
- **MUST** que la migración sea compatible con la versión anterior de la app (expand/contract): la app N-1 debe funcionar con el esquema N.
- **MUST** probar la migración en CI contra una BD real (Testcontainers) con datos representativos, y validar `flyway validate`/checksums.
- **MUST** que la migración use un usuario con DDL distinto del usuario de runtime (mínimo privilegio).
- **MUST** hacer backup o punto de restauración verificable antes de migraciones destructivas en entornos no efímeros.
- **MUST NOT** editar migraciones ya aplicadas; se corrige con una nueva versión.
- **MUST NOT** usar `flyway clean` ni `baselineOnMigrate` fuera de entornos efímeros.
- **SHOULD** fijar `lock_timeout` y ejecutar índices con `CONCURRENTLY` en PostgreSQL.

## deployment-verification-and-smoke

- **MUST** esperar al rollout (`kubectl rollout status --timeout=...`) antes de declarar éxito; un `apply` sin espera no verifica nada.
- **MUST** ejecutar smoke tests tras el despliegue: endpoint de salud (readiness), una operación de lectura y una escritura idempotente de extremo a extremo con datos sintéticos.
- **MUST** comprobar que la versión desplegada es la esperada (digest/`/actuator/info`), para no probar la versión anterior por error.
- **MUST** que el smoke tenga timeout y reintentos acotados, y falle el job si no pasa; el fallo dispara `rollback-strategy`.
- **SHOULD** consultar las métricas RED del servicio durante una ventana corta tras el despliegue (tasa de error y latencia) con umbrales del SLO.
- **MUST NOT** usar `sleep` fijo como verificación; sondear con condición y timeout.
- **MUST NOT** ejecutar smoke destructivo ni con datos reales en producción.

## ephemeral-preview-environments

- **MUST** crear un namespace por PR (`preview-pr-<n>`) con `ResourceQuota`, `LimitRange` y `NetworkPolicy` deny-by-default.
- **MUST** desplegar la imagen del PR por digest y los mismos manifiestos/chart que producción con valores de preview.
- **MUST** destruir el entorno al cerrar el PR y con un TTL (p. ej. 24 h) como red de seguridad.
- **MUST** usar datos sintéticos y secretos efímeros propios del preview; nunca datos reales ni secretos de otros entornos.
- **MUST NOT** exponer previews a Internet sin autenticación.
- **MUST NOT** permitir previews desde forks sin aprobación (ejecutan código no confiable).
- **SHOULD** limitar previews concurrentes por repositorio y etiquetar recursos con `pr`, `owner` y `expires-at` para FinOps.
- **SHOULD** ejecutar en el preview: smoke, contratos y perf corto (`deployment-verification-and-smoke`, `performance-gate`).

## github-actions

- **MUST** fijar toda acción y workflow reutilizable de terceros por SHA de commit completo (40 hex), con el tag en comentario.
- **MUST** declarar `permissions:` de nivel superior mínimo (`contents: read`) y ampliar por job.
- **MUST** autenticarse en la nube con OIDC (`id-token: write` solo en el job que lo necesita); sin claves de acceso de larga vida en secrets.
- **MUST** restringir la confianza del lado de la nube a repo + entorno/rama (claim `sub`), no a toda la organización.
- **MUST** centralizar lógica repetida en workflows reutilizables (`on: workflow_call`) llamados con `uses:` fijado por SHA.
- **MUST** proteger despliegues con `environment:` (revisores requeridos, ramas permitidas) para dev/staging/prod.
- **MUST NOT** interpolar entradas no confiables (`github.event.pull_request.title`, nombres de rama) directamente en `run:`; pasarlas por `env:`.
- **MUST NOT** usar `pull_request_target` para ejecutar código de la PR con secretos.
- **SHOULD** usar runners efímeros (un job, una VM/contenedor) para builds sensibles; self-hosted solo efímeros y aislados.
- **SHOULD** cachear dependencias con clave que incluya el hash del lockfile, y usar `strategy.matrix` con `fail-fast` decidido a propósito.
- **SHOULD** definir `concurrency:` para cancelar ejecuciones obsoletas de PR y serializar despliegues.

## performance-gate

- **MUST** definir umbrales como código (p95/p99 de latencia, tasa de error, throughput mínimo) derivados del SLO, versionados con el servicio.
- **MUST** ejecutar JMeter (D19) en modo no-GUI (`-n`) contra el entorno efímero o staging, nunca contra producción.
- **MUST** fallar el job si se superan los umbrales o si la regresión frente a la línea base supera el margen acordado.
- **MUST** calentar la JVM (warm-up) y descartar ese tramo de las métricas.
- **SHOULD** comparar contra el último resultado de `main` (línea base almacenada como artefacto) y no solo contra umbrales absolutos.
- **SHOULD** ejecutar la prueba larga (soak) en nightly y una prueba corta (smoke de carga) en cada merge.
- **MUST NOT** interpretar resultados de runners compartidos como capacidad real: son tendencia relativa; la capacidad se modela aparte (`capacity-and-load-modeling`).

## pipeline-architecture

- **MUST** separar CI (construir, probar, publicar artefacto) de CD (promover). CD no reconstruye: promueve el mismo digest.
- **MUST** construir el artefacto una sola vez y promoverlo por digest inmutable (`sha256:`), nunca por tag mutable como `latest`.
- **MUST** ordenar etapas de lo barato a lo caro: lint/unit, build, seguridad estática, integración/contrato, imagen y escaneo, preview, rendimiento, promoción.
- **MUST** hacer que cada gate sea bloqueante y devuelva código de salida distinto de cero; ningún gate "informativo" en la rama principal sin excepción registrada.
- **MUST** que el pipeline sea la única vía a entornos compartidos; sin despliegues manuales desde portátiles.
- **SHOULD** paralelizar jobs independientes y usar `needs:` solo para dependencias reales.
- **SHOULD** que el pipeline sea reproducible en local (`make verify` o equivalente) para depurar sin hacer push.
- **MUST NOT** mezclar en un mismo job build y despliegue ni compartir credenciales de despliegue con jobs de PR de forks.

## pipeline-observability-and-dora

- **MUST** capturar las cuatro métricas DORA: frecuencia de despliegue, lead time de cambios, tasa de fallo de cambios y tiempo de recuperación (MTTR). Definiciones por proyecto, escritas en el repo.
- **MUST** emitir un evento por despliegue (servicio, versión/digest, entorno, resultado, timestamp, SHA) desde el propio pipeline, incluidos los rollbacks.
- **MUST** definir "fallo de cambio" (rollback, hotfix o incidencia atribuida a un despliegue) y enlazarlo a la gestión de incidentes (`incident-management-and-postmortems`).
- **SHOULD** medir además duración por etapa, tiempo en cola de runners, tasa de reintentos y tests inestables (flakiness).
- **SHOULD** exportar a la plataforma de observabilidad (OpenTelemetry/Prometheus) y mostrar en un dashboard como código.
- **MUST NOT** incluir secretos, datos personales ni nombres de personas en eventos o métricas.
- **MUST NOT** usar las métricas DORA como objetivo individual o ranking de equipos (ley de Goodhart).

## quality-gates

- **MUST** ejecutar en CI `./mvnw verify` (unitarios + integración con Testcontainers, D19); el fallo bloquea el merge.
- **MUST** ejecutar las reglas ArchUnit como parte de los tests (`policies/archunit/`).
- **MUST** fallar el build si la cobertura de líneas/ramas en código nuevo baja del umbral acordado (umbral por proyecto; sugerido 80 % en código nuevo).
- **SHOULD** ejecutar PIT (mutación) sobre módulos de dominio con umbral explícito, en nightly si es lento.
- **MUST** aplicar formato y checkstyle/Spotless en modo `check`, no `apply`, en CI.
- **MUST NOT** desactivar tests (`@Disabled`, `-DskipTests`) para pasar el gate; un test inestable se arregla o se pone en cuarentena con issue y fecha.
- **MUST NOT** bajar umbrales para que pase un PR; cambiar un umbral requiere PR propio.
- **SHOULD** publicar informes (JaCoCo, Surefire) como artefacto del job.

## release-versioning-changelog

- **MUST** usar SemVer 2.0.0 para librerías y servicios: MAJOR rompe compatibilidad, MINOR añade, PATCH corrige.
- **MUST** derivar el siguiente número de Conventional Commits (`feat`, `fix`, `feat!`/`BREAKING CHANGE:`), no de decisión manual ad hoc.
- **MUST** crear la release desde `main`, con tag anotado `vX.Y.Z` sobre el commit que pasó los gates; el tag no se mueve ni se reescribe.
- **MUST** que el artefacto lleve la versión y el SHA (labels OCI `org.opencontainers.image.version` y `.revision`) y se identifique por digest.
- **MUST** generar el changelog automáticamente (agrupado por tipo) y publicarlo en las notas de release.
- **SHOULD** versionar Maven con `revision` (CI-friendly) y evitar commits de "bump version" manuales.
- **MUST NOT** reutilizar ni sobrescribir una versión publicada; un error se corrige con un PATCH nuevo.
- **MUST NOT** publicar `-SNAPSHOT` a entornos distintos de dev.

## rollback-strategy

- **MUST** poder volver a la versión anterior redesplegando su digest inmutable, sin recompilar (`pipeline-architecture`).
- **MUST** conservar el digest y la configuración de la última versión estable por entorno (registro de despliegues).
- **MUST** que cada release sea compatible con la anterior a nivel de esquema y mensajes (expand/contract, `backward-compatibility-rules`); el rollback de app no revierte la BD.
- **MUST** automatizar el rollback ante fallo de `deployment-verification-and-smoke` y documentar el disparo manual (workflow `workflow_dispatch` con el digest como entrada).
- **SHOULD** desacoplar despliegue de activación con feature flags: apagar el flag es el rollback más rápido.
- **SHOULD** preferir roll-forward cuando el fallo es un bug pequeño y la migración ya es irreversible; decidirlo con criterio explícito.
- **MUST NOT** revertir migraciones destructivas ejecutando "down" improvisados; usar backup/restauración probados (`backup-vault-immutability-and-restore-tests`).
- **MUST** registrar el rollback (`record-deployment` en Pact, evento de despliegue para DORA).

## security-gates

- **MUST** ejecutar SAST (Semgrep con las reglas de `policies/semgrep/`), detección de secretos y SCA en cada PR.
- **MUST** escanear la imagen con Trivy y Grype y el árbol de dependencias con OWASP Dependency-Check (D17); fallar en severidad CRITICAL/HIGH con arreglo disponible.
- **MUST** escanear IaC (Checkov/Conftest, `terraform validate`) antes de cualquier `plan`.
- **MUST** generar SBOM CycloneDX por build, subirlo a Dependency-Track y firmar la imagen (cosign) tras pasar los gates.
- **MUST** registrar excepciones como VEX/archivo de ignorados con motivo, dueño y caducidad; nunca ignorar en silencio.
- **MUST NOT** usar licencias de pago por defecto (D16); Xray es opcional (D17).
- **MUST NOT** exponer secretos a jobs de PR de forks.
- **SHOULD** ejecutar escaneos programados (nightly) además de en PR: aparecen CVEs nuevas sin cambio de código.
