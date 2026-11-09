# Estándares · 28-local-kubernetes

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## aws-emulation

- **MUST** preferir el emulador oficial o de código abierto sin cuenta: DynamoDB Local (`amazon/dynamodb-local`) para DynamoDB, MinIO para S3, Redis para ElastiCache, Strimzi para MSK.
- **MUST** tratar LocalStack como opcional y no apoyar el entorno local en él: desde el 2026-03-23 LocalStack ya no publica la edición Community; solo hay una imagen única que exige cuenta y auth token, y el plan gratuito (Hobby) es para uso no comercial (https://blog.localstack.cloud/the-road-ahead-for-localstack/, verificado el 2026-11-08). En un proyecto corporativo choca con D16: usarlo exige un plan de pago y una decisión explícita en un ADR.
- **MUST** acceder a los emuladores por configuración de endpoint (`endpoint-override`), nunca con ramas `if (local)` en el código de dominio.
- **MUST** que las credenciales del emulador sean de ejemplo (`example`/`changeme`) y vivan solo en el perfil local.
- **MUST** listar en el README del perfil qué NO se reproduce (ver `local-parity-matrix`): Global Tables fiables, throttling, backups y consistencia eventual en DynamoDB; replicación y Object Lock completo en S3; Multi-AZ en Redis.
- **SHOULD** probar contratos (esquemas, claves, condiciones de escritura) en local y dejar rendimiento, límites de cuota y resiliencia como "no verificado".
- **MUST NOT** afirmar que un comportamiento está comprobado en AWS por haber pasado contra un emulador.
- **MUST NOT** emular IAM de AWS: en local la autorización es RBAC de Kubernetes.

## cluster-tooling

- **MUST** usar kind por defecto (ADR-0034); k3d solo como alternativa documentada y justificada en el README del proyecto.
- **MUST** definir el clúster en un fichero versionado (`deploy/local/kind-config.yaml`), nunca con flags sueltos en comandos de wiki.
- **MUST** fijar la versión de nodo (`image: kindest/node:<tag>`) alineada con la versión de Kubernetes objetivo de EKS.
- **MUST** exponer un registro local para el bucle de desarrollo (patrón oficial de kind con `certs.d`), en vez de `kind load` en cada cambio.
- **MUST** envolver crear/destruir/reiniciar en `make local-up`, `make local-down`, `make local-reset` idempotentes.
- **SHOULD** usar un clúster por proyecto con nombre explícito (`kind create cluster --name <project>`), nunca el contexto `kind-kind` genérico.
- **SHOULD** comprobar `kubectl config current-context` antes de aplicar nada (evitar aplicar contra un clúster ajeno).
- **MUST NOT** apuntar los scripts locales a contextos que no empiecen por `kind-` o `k3d-`.
- **MUST NOT** presentar el clúster local como evidencia de que el despliegue funciona en AWS.

## data-seeding-and-demo-data

- **MUST** que los datos sean sintéticos: generados o escritos a mano, nunca volcados de un entorno real, ni anonimizados a medias.
- **MUST** que el seed sea idempotente: reejecutarlo no duplica ni falla (`INSERT ... ON CONFLICT DO NOTHING`, `PutItem` con clave determinista).
- **MUST** separar esquema (migraciones) de datos de demo; el seed vive en un perfil o carpeta propia y nunca se empaqueta en la imagen de producción.
- **MUST** respetar la regla de no doble escritura (4.5): cada dato se siembra en un único almacén, el de su agregado.
- **MUST** ejecutar el seed como `Job` de Kubernetes con `restartPolicy: OnFailure` y `backoffLimit` acotado, tras `readiness` de la base de datos.
- **SHOULD** usar semilla fija en generadores aleatorios para que la demo sea reproducible.
- **SHOULD** dimensionar el volumen al perfil (`minimal`: cientos de filas; `full`: miles) según `resource-budgets`.
- **MUST NOT** incluir correos, nombres, teléfonos ni documentos reales; usar dominios `example.com` y credenciales `example`/`changeme`.
- **MUST NOT** ejecutar el seed contra endpoints que no sean el clúster local.

## dev-loop

- **MUST** elegir una sola herramienta por proyecto (Tilt o Skaffold) y documentarla; no mantener ambos ficheros.
- **MUST** reutilizar los mismos manifiestos/Helm/Kustomize que usará GitOps (`helm-standards`, `kustomize-overlays`) con un overlay `local`; no escribir YAML paralelo solo para el bucle.
- **MUST** construir con el mismo Dockerfile multistage que CI (`docker-multistage`) y publicar al registro local.
- **MUST** definir `make dev` como único punto de entrada.
- **SHOULD** limitar el live-update a recursos estáticos o classes recargables; para Java el rebuild de imagen con caché de capas es el camino fiable.
- **SHOULD** declarar en el fichero qué recursos arrancan por defecto, respetando el perfil de `local-profiles`.
- **MUST NOT** commitear credenciales ni tokens en el Tiltfile/skaffold.yaml; usar secretos de ejemplo (`changeme`) para el perfil local.
- **MUST NOT** ejecutar el bucle contra un contexto que no sea de clúster local.

## devcontainer-integration

- **MUST** que el devcontainer incluya el tooling del bucle local: Docker (docker-in-docker o socket del host), kind, kubectl, Helm, Kustomize y Tilt o Skaffold según `dev-loop`.
- **MUST** fijar versiones de las herramientas (feature o descarga con checksum); no usar `latest`.
- **MUST** que `make local-up` funcione dentro del devcontainer sin pasos manuales previos.
- **MUST** documentar el requisito de recursos del contenedor (ver `resource-budgets`); docker-in-docker anida un segundo nivel de consumo.
- **SHOULD** preferir el socket del host cuando el equipo acepta compartir el daemon; documentar el compromiso de aislamiento.
- **SHOULD** instalar extensiones de editor solo si aportan al flujo (YAML, Kubernetes), sin telemetría adicional.
- **MUST NOT** montar `~/.aws` ni exportar credenciales AWS al devcontainer: en local no hace falta ni se despliega (ADR-0004).
- **MUST NOT** incluir secretos en `devcontainer.json`; los valores locales son `example`/`changeme`.
- **MUST NOT** publicar puertos de dashboards (Grafana, Argo CD) a la red externa; solo `localhost`.

## local-gitops

- **MUST** ser opt-in: `make local-gitops` separado de `make local-up`; ningún perfil lo activa por defecto.
- **MUST** que Argo CD apunte a un repositorio git accesible desde el clúster (git server local en el clúster o un `file`/bare repo montado).
- **MUST** usar el patrón app-of-apps y los mismos manifiestos Kustomize que el perfil local, para no mantener dos fuentes de verdad.
- **MUST** `syncPolicy.automated` con `prune: true` y `selfHeal: true` solo en el clúster local; documentar que en los entornos reales la política la decide la guía de promoción.
- **MUST** que el destino sea `https://kubernetes.default.svc` (el clúster kind), nunca un clúster remoto.
- **SHOULD** ejecutar `policies/opa-conftest/argocd-gitops.rego` sobre las `Application` antes de aplicarlas.
- **MUST NOT** guardar credenciales de repositorio reales; usar valores `example`/`changeme`.
- **MUST NOT** usar `kubectl apply` manual sobre recursos gestionados por Argo CD (provoca drift).
- **MUST NOT** reproducir ApplicationSets multi-clúster ni multi-región: no se representan en local.

## local-parity-matrix

- **MUST** que el proyecto incluya una tabla AWS / local / no reproducido derivada de `catalog/parity-matrix.yaml`, sin quitar filas que usen sus servicios.
- **MUST** usar estas equivalencias por defecto: EKS = kind (ADR-0034, k3d alternativa); Aurora PostgreSQL = CloudNativePG; DynamoDB = DynamoDB Local; MSK = Strimzi; S3 = MinIO; ElastiCache = Redis; ALB + Route 53 = Istio gateway (Gateway API); KMS / Secrets Manager = Vault en modo dev; IAM / IRSA = RBAC; CloudWatch = Prometheus, Grafana, Loki, Tempo.
- **MUST** declarar como no reproducido: WAF, Shield y CloudFront (todo); multi-región y DR (solo simulacro documental, ver `dr-tabletop-exercises`); nodos gestionados y autoscaling real de EKS; failover global de Aurora; replicación entre regiones de MSK y S3; claves multi-región; modelo de identidades AWS; DNS y balanceo gestionados.
- **MUST** recordar que Testcontainers sigue siendo necesario: el clúster local ejecuta el sistema completo, no sustituye los tests de integración.
- **SHOULD** enlazar cada fila a la prueba que sí cubre el comportamiento reproducible.
- **MUST NOT** presentar "funciona en local" como evidencia de comportamiento en AWS.

## local-profiles

- **MUST** ofrecer dos perfiles con nombre: `minimal` y `full`, seleccionables con `make local-up PROFILE=minimal|full`.
- **MUST** que `minimal` contenga solo: el servicio, Postgres (CloudNativePG u operador equivalente) y DynamoDB Local (imagen oficial de AWS, sin cuenta ni licencia).
- **MUST** que `full` añada: Kafka (Strimzi), Vault en modo dev, Istio con Gateway API, y observabilidad (Prometheus, Grafana, Loki, Tempo). MinIO y Redis solo si el servicio los usa.
- **MUST** que el servicio arranque en `minimal` sin las piezas de `full` (feature toggles / adaptadores nulos documentados), o declarar explícitamente que no es posible.
- **MUST** documentar en cada perfil qué NO reproduce respecto a AWS (ver `local-parity-matrix`).
- **SHOULD** declarar requisitos de recursos por perfil (`resource-budgets`).
- **MUST NOT** activar `full` por defecto.
- **MUST NOT** usar Vault en modo dev ni claves de ejemplo fuera del clúster local; el modo dev es solo local.

## resource-budgets

- **MUST** documentar por perfil la RAM y CPU mínimas de la máquina. Los valores numéricos son hipótesis a medir, no cifras garantizadas.
- **MUST** que `minimal` (servicio, Postgres, DynamoDB Local) sea el perfil por defecto y quepa en un portátil de gama media.
- **MUST** que todo pod local declare `resources.requests` y `resources.limits`; sin límites un pod puede tumbar el nodo kind.
- **MUST** fijar `requests` bajos y `limits` moderados en el overlay local; no reutilizar los del diseño para AWS.
- **SHOULD** limitar réplicas a 1 en local (Kafka, Postgres, Vault dev) y declararlo como no reproducción de HA.
- **SHOULD** reducir retención y scrape interval en Prometheus/Loki/Tempo en `full`.
- **SHOULD** limitar WSL2 con `.wslconfig` (`memory`, `processors`) y avisar si se supera.
- **MUST NOT** activar `full` por defecto ni sumar componentes a `minimal` sin actualizar la tabla de presupuestos.
- **MUST NOT** afirmar que un presupuesto local demuestra el dimensionamiento real.
