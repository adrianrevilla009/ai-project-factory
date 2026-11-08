# Estándares · 13-kubernetes-and-istio

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## authorization-policies

- **MUST** partir de deny-all por namespace (`AuthorizationPolicy` sin `rules`) y añadir `ALLOW` explícitos.
- **MUST** identificar al llamante por `source.principals` (identidad SPIFFE, requiere mTLS STRICT), no por IP ni namespace solamente.
- **MUST NOT** usar `principals: ["*"]` ni `allow` sin `from`.
- **SHOULD** limitar por `operation` (`methods`, `paths`) en endpoints sensibles.
- **SHOULD** usar `DENY` para excepciones claras (p. ej. `/actuator/*` desde fuera) y `AUDIT`/`CUSTOM` solo si hay backend definido.
- **MUST** probar cada política (llamada permitida y llamada denegada esperada → 403).
- **MUST NOT** validar JWT solo en la malla ignorando la validación en el servicio (defensa en profundidad).

## autoscaling

- **MUST** que el workload tenga `resources.requests` correctos antes de activar HPA: el porcentaje se calcula sobre requests.
- **MUST** definir `minReplicas >= 2` en prod y `maxReplicas` acotado por cuota y presupuesto.
- **MUST NOT** combinar HPA y VPA sobre la misma métrica (cpu/memory) del mismo workload; VPA en modo `Off`/recomendación si coexisten.
- **SHOULD** usar HPA `autoscaling/v2` con `behavior` (estabilización de bajada, límites de subida) para evitar flapping.
- **SHOULD** escalar con KEDA por eventos (lag de consumer group Kafka, longitud de cola) en consumidores; el máximo de réplicas **MUST NOT** superar las particiones del topic.
- **MUST** considerar el arranque JVM: usar `startupProbe` y warm-up; escalar tarde por arranque lento es un riesgo.
- **MUST** que el escalado de pods tenga nodos disponibles (Cluster Autoscaler/Karpenter) y headroom; si no, los pods quedan `Pending`.
- **SHOULD** validar con pruebas de carga (ver `performance-gate`) que el escalado responde antes de saturar.
- Local: kind no reproduce autoscaling de nodos; metrics-server y KEDA sí pueden instalarse.

## backup-and-restore

- **MUST** que el estado deseado esté en Git (GitOps); Velero cubre estado que Git no tiene: PVC, CRs creados por operators, Secrets generados.
- **MUST** programar backups con `Schedule` y `ttl` (retención) explícitos; **MUST NOT** depender de backups manuales.
- **MUST** almacenar los backups fuera del clúster, en otro bucket/cuenta o región, con cifrado y acceso mínimo; en local, MinIO.
- **MUST** hacer una prueba de restauración periódica a un clúster limpio y registrar RTO medido; un backup sin restore probado no cuenta.
- **MUST** tratar los datos de aplicación con el mecanismo nativo de la base de datos (WAL/PITR) además de, no en lugar de, snapshots de volúmenes.
- **SHOULD** excluir namespaces de sistema y recursos regenerables (`excludedNamespaces`, labels de exclusión).
- **SHOULD** alertar si un backup falla o no hay uno reciente.
- **MUST NOT** guardar credenciales del bucket en el manifiesto: usar identidad de nube o Secret gestionado (ver `cluster-addons-baseline`).
- Honestidad: restauración validada solo si se ejecutó; la fábrica no ejecuta backups en AWS, preparado para AWS, no verificado en real.
- Local: no se reproducen snapshots de EBS; Velero con plugin de filesystem y MinIO es una aproximación.

## canary-and-traffic-splitting

- **MUST** desplegar la versión nueva como Deployment aparte con etiqueta `version`, sin tocar la estable.
- **MUST** repartir con pesos explícitos que sumen 100 y empezar con porcentaje bajo (p. ej. 5 %).
- **MUST** definir antes criterios de promoción y de rollback (tasa de error, latencia p99) medidos en métricas de la malla.
- **MUST** poder volver a 100 % estable con un solo cambio de manifiesto.
- **SHOULD** usar `HTTPRoute.backendRefs[].weight` (Gateway API) y reservar `VirtualService` para lo que no cubra (comprobar al fijar la versión).
- **SHOULD** usar mirroring para probar con tráfico real sin efectos visibles, solo en operaciones idempotentes y de lectura.
- **MUST NOT** hacer canary con efectos secundarios no idempotentes duplicados (mirroring de pagos).
- **SHOULD** valorar un controlador de entrega progresiva OSS (p. ej. Argo Rollouts o Flagger; comprobar compatibilidad) frente a ediciones manuales.

## cluster-addons-baseline

- **MUST** mantener una lista explícita de addons con versión fijada, dueño y namespace: CNI, CSI, CoreDNS, metrics-server, cert-manager, external-dns, external-secrets, ingress/gateway (ver `gateway-api`).
- **MUST** instalar los addons por GitOps/IaC, nunca con `kubectl apply` manual; **MUST NOT** usar manifiestos remotos con `latest`.
- **MUST** ejecutar los addons en el pool de sistema con requests, PDB y réplicas >= 2 (ver `workload-baseline`).
- **MUST** dar a cada addon que llama a la nube una identidad propia de mínimo privilegio (ver `rbac-and-service-accounts`); external-dns solo sobre las zonas que gestiona.
- **MUST NOT** guardar secretos en Git: external-secrets lee de Vault OSS (o gestor de la nube) y crea el Secret; ver `injection-patterns`.
- **SHOULD** usar cert-manager con un issuer interno (CA propia/Vault PKI) y certificados con renovación automática; alertar antes de caducar.
- **SHOULD** versionar CRDs de addons y actualizarlos antes que sus controladores (ver `cluster-upgrades-and-drift`).
- **MUST** declarar qué NO se reproduce en local: sin Route 53, sin ACM/KMS; usar CoreDNS/dnsmasq, CA self-signed y Vault dev.

## cluster-topology

- **MUST** separar producción de no-producción en clústeres distintos (el límite de blast radius es el clúster, no el namespace).
- **MUST** documentar en un ADR del proyecto el número de clústeres, su propósito y el criterio de crecimiento.
- **MUST** definir cada clúster como código (Terraform para EKS, ver `eks-networking`); **MUST NOT** crear clústeres a mano.
- **SHOULD** empezar con el mínimo: un clúster por entorno (dev, staging, prod) y añadir regiones/cells solo con requisito de RTO/RPO o residencia de datos.
- **SHOULD** alojar las herramientas de plataforma (GitOps, observabilidad, Vault) en un clúster o cuenta de gestión propio si el proyecto lo justifica.
- **SHOULD** usar nombres predecibles: `<proyecto>-<entorno>-<region>`.
- **MUST** declarar qué NO se reproduce en local: kind/k3d son un único nodo/clúster; sin zonas de disponibilidad reales, sin balanceador cloud, sin IAM de nube.
- **MUST NOT** afirmar "listo para producción en AWS": estado = preparado para AWS, no verificado en real (ADR-0004).

## cluster-upgrades-and-drift

- **MUST** mantener el clúster dentro de una versión de Kubernetes con soporte; revisar el calendario oficial cada trimestre (comprobar ventanas de soporte de EKS).
- **MUST** actualizar de una versión menor cada vez, en este orden: plano de control, addons, nodos; probar antes en dev y staging.
- **MUST** revisar APIs deprecadas/eliminadas antes de cada upgrade con una herramienta de detección (p. ej. pluto o kubent, OSS; comprobar al fijar la versión) en CI.
- **MUST** tener PDB y topology spread (ver `workload-baseline`) para que el drain de nodos no corte servicio.
- **SHOULD** actualizar nodos reemplazándolos (nuevos pools/AMI) en lugar de parchear in-place.
- **MUST** definir el estado deseado en Git/Terraform; el drift se detecta con `terraform plan` programado y con la comparación de GitOps (ver `drift-and-self-heal-policy`).
- **MUST NOT** hacer cambios manuales con `kubectl edit` en prod; si es una emergencia, registrar y llevar el cambio a Git en 24 h.
- **MUST** tener un plan de rollback documentado (el plano de control EKS no admite downgrade: el rollback es restaurar o recrear; ver `backup-and-restore`).
- **MUST** que la fábrica solo valide estáticamente: no ejecuta upgrades (ADR-0004).

## cost-visibility

- **MUST** exigir en todo workload las etiquetas `app.kubernetes.io/name`, `team` y `env` (nombres propios de la organización, ajustables).
- **MUST** usar OpenCost (OSS) con Prometheus como fuente de métricas; sin licencias de pago por defecto (D16).
- **MUST** fijar `requests` en todos los pods: sin requests la asignación de coste es incorrecta.
- **SHOULD** separar el coste de recursos ociosos (`__idle__`) del coste atribuido.
- **SHOULD** revisar mensualmente los workloads con mayor diferencia entre request y uso real.
- **MUST NOT** presentar cifras de OpenCost como coste facturado en AWS; decir "estimación".
- **MUST NOT** usar etiquetas con datos personales.

## gateway-api

- **MUST** preferir `Gateway` + `HTTPRoute` (API estándar) sobre `Ingress` en proyectos nuevos; Istio la implementa con `gatewayClassName: istio`.
- **MUST** separar roles: el equipo de plataforma posee `Gateway`; los equipos de servicio poseen sus `HTTPRoute`.
- **MUST** restringir qué namespaces pueden adjuntar rutas con `allowedRoutes`.
- **MUST** terminar TLS en el `Gateway` con un `Secret` gestionado por cert-manager; nunca certificados en el repo.
- **SHOULD** usar `VirtualService`/`DestinationRule` de Istio solo para lo que Gateway API no cubra todavía (comprobar cobertura vigente).
- **MUST NOT** mezclar `Ingress` y `Gateway` para el mismo host.

## helm-standards

- **MUST** un chart genérico de servicio reutilizable (library o chart base) en lugar de copiar templates por servicio.
- **MUST** incluir `values.schema.json` para validar values y fallar pronto.
- **MUST** versionar el chart (`version`, SemVer) separado de `appVersion`; **MUST NOT** publicar charts con versión mutable.
- **MUST** pasar `helm lint` y `helm template | kubeconform` (o equivalente) en CI.
- **MUST NOT** guardar secretos en `values.yaml`; usar referencias a Secrets creados por external-secrets o Vault (ver `cluster-addons-baseline`).
- **MUST** exponer en values: imagen (repositorio + tag/digest), resources, probes, réplicas, securityContext con defaults seguros del `workload-baseline`.
- **SHOULD** limitar la lógica en templates: sin `lookup` ni condicionales anidados profundos; helpers en `_helpers.tpl`.
- **SHOULD** fijar charts de terceros por versión exacta y revisar sus values; **MUST NOT** usar `latest` ni rangos abiertos.
- **SHOULD** usar un values por entorno (`values-prod.yaml`) con solo las diferencias.
- **MUST** pensar en el diff: los hooks de Helm y `lookup` complican GitOps; documentarlos si se usan.

## ingress-and-egress-gateways

- **MUST** desplegar el gateway de ingress en un namespace propio (`istio-ingress`), separado de `istio-system`, con su propio escalado y PDB.
- **MUST** definir la entrada con Gateway API (ver `gateway-api`); `Gateway` de Istio clásico solo si hay una carencia documentada.
- **MUST** configurar `outboundTrafficPolicy.mode: REGISTRY_ONLY` en entornos con requisito de egress controlado y declarar cada destino externo con `ServiceEntry`.
- **SHOULD** enrutar por un gateway de egress los destinos externos que requieran auditoría o IP fija.
- **MUST** aplicar `AuthorizationPolicy` al propio gateway (qué hosts y rutas se aceptan).
- **MUST NOT** exponer dashboards de administración (Kiali, Prometheus) por el gateway público.
- **MUST** indicar que en local (kind/minikube) el balanceador es simulado (p. ej. port-forward o MetalLB) y que el balanceador real de AWS no se reproduce: preparado para AWS, no verificado en real.

## istio-upgrades-and-ops

- **MUST** fijar la versión de Istio en el repositorio (Helm values / IstioOperator-equivalente) y comprobar la matriz de compatibilidad con la versión de Kubernetes (comprobar matriz vigente).
- **MUST** actualizar en una versión menor cada vez y revisar notas de versión y cambios incompatibles.
- **MUST** preferir upgrade canary por **revisión**: instalar `istiod` nuevo en paralelo, migrar namespaces cambiando la etiqueta `istio.io/rev` y reiniciar sus pods; retirar el antiguo al final (comprobar comandos exactos de la versión).
- **MUST** ejecutar `istioctl x precheck` antes (comprobar nombre del subcomando) y `istioctl analyze` después.
- **MUST** tener `istiod` con varias réplicas, PDB y `requests` definidos.
- **SHOULD** actualizar primero un namespace de prueba y observar métricas antes de producción.
- **MUST** probar el rollback: la etiqueta de revisión anterior debe seguir disponible hasta validar.
- **MUST NOT** hacer upgrade in-place en producción sin plan de vuelta atrás.
- **MUST** declarar que los upgrades se ensayan en local (kind) y que no se verifican en AWS.

## kustomize-overlays

- **MUST** estructura `base/` (común) + `overlays/<env>/` (solo diferencias); **MUST NOT** duplicar la base en cada overlay.
- **MUST** que los overlays modifiquen con patches pequeños (strategic merge o JSON 6902) y `images:` para versiones; **MUST NOT** copiar ficheros enteros.
- **MUST** que `kustomize build overlays/<env>` produzca YAML válido y pase kubeconform en CI para cada entorno.
- **MUST NOT** incluir secretos en `secretGenerator` con valores reales; usar external-secrets/Vault (ver `cluster-addons-baseline`).
- **SHOULD** fijar `namespace`, `labels` comunes y `nameSuffix`/`namePrefix` solo si hacen falta; evitarlos si rompen referencias.
- **SHOULD** usar `configMapGenerator` con hash para forzar rollout al cambiar config.
- **SHOULD** no mezclar Helm y Kustomize sin motivo: si se hace, `helm template` a base y parchear, documentado.
- **MUST** mantener las diferencias entre entornos pequeñas y visibles en un diff (paridad dev/prod).

## mesh-observability

- **MUST** recoger las métricas estándar de Istio (p. ej. `istio_requests_total`, `istio_request_duration_milliseconds`) en Prometheus; nombres a confirmar (comprobar según versión).
- **MUST** instalar Kiali (OSS) solo como herramienta interna; acceso autenticado y fuera del gateway público.
- **MUST** propagar cabeceras de trazado (W3C `traceparent`/B3) desde la aplicación: la malla no puede unir spans si la app no las reenvía.
- **SHOULD** configurar muestreo de trazas bajo por defecto (p. ej. 1 %) y subirlo temporalmente al depurar.
- **SHOULD** definir alertas sobre la tasa de 5xx y la latencia p99 por servicio, ligadas a SLO.
- **MUST NOT** registrar cuerpos de petición ni datos personales en los access logs de Envoy.
- **MUST NOT** dejar el dashboard de Kiali con la configuración de demo en entornos compartidos.

## mesh-vs-app-resilience

- **MUST** asignar cada mecanismo a una sola capa y documentarlo: reintentos en una, no en ambas.
- **MUST NOT** activar reintentos en la malla (`retries`) y en el cliente (Resilience4j, Spring Retry) para la misma llamada: los intentos se multiplican (3 x 3 = 9).
- **MUST** reintentar solo operaciones idempotentes; para POST exigir clave de idempotencia (ver `idempotency-keys`).
- **MUST** respetar el presupuesto de tiempo: `timeout` total >= `attempts` x `perTryTimeout` y menor que el timeout del llamante.
- **SHOULD** dejar en la malla: timeouts de borde, `outlierDetection`, límites de conexión. **SHOULD** dejar en la aplicación: fallbacks de negocio, bulkheads, degradación funcional.
- **SHOULD** limitar `retryOn` a fallos de conexión y 503 (comprobar valores admitidos).
- **MUST** definir una política por defecto de la plataforma y excepciones documentadas.

## mtls-strict-and-peer-auth

- **MUST** definir un `PeerAuthentication` de malla en el namespace raíz (`istio-system`) con `mtls.mode: STRICT`.
- **MUST** usar `PERMISSIVE` solo como paso temporal de migración, con fecha de retirada anotada.
- **MUST NOT** usar `mode: DISABLE` salvo excepción por puerto con ADR (p. ej. un agente de métricas externo).
- **MUST** completar la inyección/inclusión en la malla de los clientes antes de pasar a STRICT; si no, se cortan peticiones.
- **SHOULD** acompañar mTLS con `AuthorizationPolicy`: mTLS autentica, no autoriza.
- **SHOULD** apoyarse en la rotación automática de certificados de Istio y no montar certificados propios (ver `crypto-tls-mtls-key-rotation`).
- **MUST** documentar qué se reproduce en local (mTLS funciona igual en kind/minikube) y qué no (integración con CA de AWS: preparado para AWS, no verificado en real).

## multi-cluster-and-dr

- **MUST** partir de los objetivos RTO/RPO por tier de servicio (ver `tier-model-and-rpo-rto`); sin objetivos no se añade complejidad multi-clúster.
- **MUST** elegir patrón por servicio y documentarlo: backup-restore, pilot light, warm standby o activo-activo (ver `multi-region-patterns`).
- **MUST** que el despliegue a todos los clústeres salga del mismo Git (ApplicationSets o equivalente) con diferencias solo en overlays.
- **MUST** resolver primero el estado: replicación de datos con la matriz definida (ver `data-replication-matrix`); **MUST NOT** doble escritura Postgres+NoSQL para "replicar".
- **MUST** diseñar la conmutación (DNS/health checks/Global Accelerator, ver bloque de redes) y el failback con runbook probado.
- **MUST** mantener identidades, secretos y certificados disponibles en el clúster de DR (Vault y Keycloak tienen su propio DR, ver `vault-and-keycloak-dr`).
- **SHOULD** ensayar la conmutación en game days (tabletop, ver `fault-injection-and-game-days`) y medir RTO.
- **SHOULD** evitar acoplar los clústeres: el fallo de uno no debe depender del plano de control del otro.
- **MUST NOT** afirmar "listo para producción en AWS" ni resiliencia multi-región verificada: la fábrica no despliega; estado = preparado para AWS, no verificado en real.
- Local: dos clústeres kind solo simulan el reparto; no reproducen latencia entre regiones ni fallos de región.

## multi-cluster-mesh

- **MUST** justificar en ADR del proyecto la necesidad multi-clúster antes de adoptarlo.
- **MUST** elegir modelo explícito: primario-remoto o multi-primario, red única o redes distintas (comprobar topologías vigentes y requisitos en la versión de Istio).
- **MUST** compartir una raíz de confianza común: CA raíz propia y CA intermedia por clúster; nunca la CA autogenerada por defecto en producción.
- **MUST** custodiar las claves de CA según `secrets-management`; nunca en el repositorio.
- **MUST** usar nombres de red y de clúster únicos y coherentes en la configuración de cada clúster.
- **SHOULD** mantener la misma versión de Istio (o dentro de la ventana soportada) en todos los clústeres.
- **MUST NOT** tratar el multi-clúster como DR completo: los datos no se replican por la malla (ver `multi-cluster-and-dr`).
- **MUST** declarar que en local solo se simula con dos clústeres kind y que el enrutado de red real en AWS no se verifica.

## namespaces-quotas-multitenancy

- **MUST** crear un namespace por equipo o servicio y entorno, con labels `team`, `env` y `pod-security.kubernetes.io/enforce`.
- **MUST** aplicar `ResourceQuota` (cpu, memory, pods, y objetos como `services.loadbalancers`) y `LimitRange` con requests/limits por defecto en cada namespace.
- **MUST** aplicar una `NetworkPolicy` default-deny (ingress y egress) y abrir solo lo necesario, incluyendo DNS.
- **MUST** asignar RBAC por namespace a grupos del IdP, no a usuarios (ver `rbac-and-service-accounts`).
- **MUST NOT** desplegar workloads de aplicación en `default` ni en `kube-system`.
- **SHOULD** generar la plantilla de namespace desde un único chart/overlay para que todos nazcan iguales.
- **SHOULD** poner cuotas de objetos (secrets, configmaps) si hay riesgo de abuso.
- **MUST** declarar que namespaces = aislamiento lógico "soft": comparten kernel, nodos y plano de control.

## node-pools-and-capacity

- **MUST** separar al menos: pool de sistema (addons, CoreDNS, controladores) y pool(s) de aplicación.
- **MUST** repartir cada pool en 3 zonas de disponibilidad cuando el entorno lo permita; **MUST NOT** fijar un pool a una sola AZ en prod.
- **MUST** usar taints/tolerations o `nodeSelector` para cargas especiales (GPU, batch, spot); el pool de sistema lleva taint para que no lo ocupen apps.
- **MUST** dejar headroom explícito (p. ej. 20-30 % de capacidad libre, valor a justificar) para absorber la pérdida de una AZ y picos antes de que escale.
- **SHOULD** usar spot/preemptibles solo para cargas tolerantes a interrupción (stateless, con PDB y `terminationGracePeriodSeconds` adecuado); **MUST NOT** ponerles bases de datos ni brokers.
- **SHOULD** preferir pocos tipos de instancia homogéneos por pool para que requests y bin-packing sean predecibles.
- **SHOULD** declarar `--max-pods`/límites de IP por nodo y comprobar que la red de pods no se agota (ver `eks-networking`).
- **MUST** definir los pools como código (Terraform); revisar versión de AMI/kubelet junto con `cluster-upgrades-and-drift`.
- Local: kind/k3d no reproduce pools, AZ ni spot; se simula con labels en nodos de prueba.

## operators

- **MUST** decidir en un ADR si el estado va en operator o en servicio gestionado; el criterio incluye RTO/RPO, equipo y coste operativo.
- **MUST** usar operators con licencia OSS (CloudNativePG, Strimzi); **MUST NOT** introducir operators de pago por defecto (D16).
- **MUST** instalar el operator en su propio namespace y los clústeres de datos en el namespace del servicio.
- **MUST** fijar la versión del operator y de sus CRDs; revisar notas de release antes de actualizar, y actualizar CRDs de forma controlada (Helm no actualiza CRDs de `crds/` por defecto).
- **MUST** definir para cada clúster: réplicas en AZ distintas (anti-affinity/topology spread), `PodDisruptionBudget`, resources, almacenamiento (StorageClass) y backups probados (ver `backup-and-restore`).
- **MUST NOT** ejecutar una única réplica de base de datos o broker en prod.
- **SHOULD** exponer métricas del operator y del clúster a Prometheus y alertar sobre lag de réplica y estado del clúster.
- **SHOULD** probar el failover y la restauración en un entorno no productivo antes de confiar en ellos.
- **MUST** respetar la regla de no doble escritura Postgres+NoSQL (4.5).
- Local: kind ejecuta los operators, pero no reproduce volúmenes EBS, multi-AZ ni rendimiento real.

## pod-security-and-admission

- **MUST** etiquetar cada namespace de aplicación con Pod Security Standards: `enforce: restricted` (o `baseline` con justificación), más `audit` y `warn` en `restricted`.
- **MUST** documentar excepciones (namespaces de sistema, CNI, mesh con init containers) con motivo y dueño.
- **MUST** desplegar un motor de políticas propio (Kyverno, OSS) para reglas que PSA no cubre: requests, probes, registros permitidos, sin `latest`.
- **MUST** introducir políticas nuevas en `Audit`, revisar informes y pasar a `Enforce` por entorno (dev, luego staging, luego prod).
- **SHOULD** valorar `ValidatingAdmissionPolicy` nativa (CEL) para reglas simples sin webhook; comprobar versión mínima de Kubernetes.
- **MUST** configurar `failurePolicy` y exclusiones de los webhooks pensando en disponibilidad: un webhook caído no debe bloquear el clúster entero ni dejarlo sin control (decisión explícita).
- **MUST NOT** aplicar políticas Enforce directamente en prod sin periodo de Audit.
- **MUST** versionar las políticas en el repo y probarlas con casos que pasan y que fallan.

## rbac-and-service-accounts

- **MUST** usar una ServiceAccount dedicada por workload; **MUST NOT** usar la `default`.
- **MUST** poner `automountServiceAccountToken: false` salvo que el pod llame a la API de Kubernetes.
- **MUST** preferir `Role`/`RoleBinding` por namespace; `ClusterRole` solo para recursos cluster-scoped o agregaciones.
- **MUST NOT** conceder `cluster-admin`, wildcards (`*`) en verbs/resources ni `secrets` get/list global a aplicaciones.
- **MUST** vincular a humanos mediante grupos del IdP (Keycloak/OIDC), no usuarios individuales.
- **MUST** revisar permisos peligrosos: `escalate`, `bind`, `impersonate`, `create pods/exec`, `create rolebindings`.
- **SHOULD** enlazar identidad de nube con IRSA o EKS Pod Identity (comprobar cuál usa el proyecto) con un rol por ServiceAccount y condición de namespace/SA en la trust policy.
- **SHOULD** usar tokens proyectados con audiencia y expiración corta; **MUST NOT** crear tokens de larga duración en Secrets.
- Local: kind no reproduce IRSA/Pod Identity; se simula con credenciales example o un emulador.

## runtime-security

- **MUST** usar Falco (licencia OSS) como detector por defecto; no adoptar productos de pago por defecto (D16).
- **MUST** desplegarlo como DaemonSet con un driver soportado por el kernel de los nodos (comprobar driver eBPF moderno vs módulo, según versión de Falco).
- **MUST** enviar las alertas a un destino persistente (Falcosidekick hacia Loki/Alertmanager/webhook), no solo a stdout del pod.
- **MUST** mantener las reglas propias en un fichero versionado (`custom-rules.yaml`) y no editar el ruleset base.
- **SHOULD** ajustar excepciones con `append`/listas de macros, nunca desactivando una regla entera sin ADR.
- **SHOULD** clasificar prioridades: `CRITICAL`/`ERROR` generan aviso a guardia; `WARNING` solo ticket.
- **MUST NOT** dar a Falco más privilegios de los que su documentación exige.

## sidecar-vs-ambient-decision

- **MUST** usar **sidecar por defecto** (ADR-0032): modo más maduro y documentado.
- **MUST** registrar en un ADR del proyecto cualquier desviación a ambient, con la verificación de madurez realizada.
- **SHOULD** valorar ambient solo si la sobrecarga de recursos por pod es un problema medido y la versión de Istio elegida lo declara estable (ambient, ztunnel y waypoint son estables desde Istio 1.24; comprobar la compatibilidad con la versión elegida).
- **MUST NOT** mezclar sidecar y ambient en un mismo namespace sin haber leído la guía de coexistencia (comprobar al fijar la versión).
- **MUST** documentar el modo elegido en el README de plataforma del proyecto.

## traffic-management

- **MUST** declarar `timeout` en cada ruta de `VirtualService`; sin él el defecto de Envoy puede no ajustarse a tu SLO (comprobar defecto vigente).
- **MUST** definir en `DestinationRule` `connectionPool` y `outlierDetection` para servicios críticos.
- **MUST** nombrar `subsets` por etiqueta de versión (`version`), no por IP.
- **MUST NOT** declarar el mismo host en varios `VirtualService` sin `gateways`/`hosts` coordinados: el resultado es indeterminado.
- **SHOULD** mantener `VirtualService` y `DestinationRule` junto al servicio que los posee.
- **SHOULD** validar con `istioctl analyze` antes de aplicar.
- **MUST** ajustar timeouts de forma coherente: timeout de ruta mayor que el del cliente HTTP interno falla primero en el cliente.

## workload-baseline

- **MUST** definir `resources.requests` de cpu y memory y `limits.memory` en cada contenedor; la memoria request = limit en servicios JVM (evita OOM por overcommit).
- **SHOULD** no fijar `limits.cpu` salvo razón medida (el throttling degrada la latencia); decisión documentada.
- **MUST** definir `readinessProbe` y `livenessProbe` (y `startupProbe` si el arranque es lento) apuntando a los endpoints de Actuator (ver `actuator-and-health`); la liveness **MUST NOT** depender de dependencias externas.
- **MUST** tener `PodDisruptionBudget` para todo servicio con `replicas >= 2`.
- **MUST** usar `topologySpreadConstraints` por zona (`topology.kubernetes.io/zone`) y por nodo en servicios con varias réplicas.
- **MUST** fijar `seccompProfile.type: RuntimeDefault`, `runAsNonRoot`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]` (ver `container-and-k8s-security`).
- **MUST** configurar `terminationGracePeriodSeconds` y apagado ordenado (`server.shutdown=graceful`).
- **MUST NOT** usar tag `latest`; fijar versión o digest.
- **SHOULD** mínimo 2 réplicas en prod.
