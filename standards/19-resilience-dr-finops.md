# Estándares · 19-resilience-dr-finops

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## application-recovery-controller-and-health-checks

- **MUST** conmutar tráfico con acciones de plano de datos. Para failover manual usar interruptores de ARC (routing controls, que gobiernan health checks de Route 53 sin comprobar salud), no cambiar pesos por la API de control.
- **MUST** guardar los endpoints del clúster ARC y credenciales de operación en el runbook, probadas fuera de la región afectada.
- **MUST** health checks "profundos" (dependencias críticas) para decidir salud, y "superficiales" para liveness; **MUST NOT** hacer que un health check público consulte la BD en cada llamada sin caché.
- **SHOULD** usar zonal shift/autoshift para sacar una AZ degradada, solo si hay capacidad N+1 (ver `multi-az-patterns`).
- **SHOULD** usar readiness checks para comparar capacidad y configuración entre regiones.
- **MUST** conmutación manual con aprobación para el failover regional; la automática por alarma solo con umbrales conservadores, por falsos positivos.
- **MUST NOT** depender de Auto Scaling u operaciones de plano de control en la ruta crítica de conmutación sin capacidad previa (ver `static-stability-and-cell-architecture`).
- **SHOULD** TTL de DNS bajo en los registros de conmutación, documentado y medido.

## backup-vault-immutability-and-restore-tests

- **MUST** copiar los backups a otra región (eu-central-1) y, preferiblemente, a otra cuenta de aislamiento.
- **MUST** activar Vault Lock con `min_retention_days` acorde a la política y `max_retention_days` para evitar costes eternos.
- **MUST** empezar en modo gobernanza o con `changeable_for_days` >= 3 (periodo de enfriamiento) y revisar antes de que sea inmutable; en modo cumplimiento, pasado ese plazo ni el titular ni AWS pueden quitar el bloqueo.
- **MUST NOT** usar retención "siempre" en recovery points de un vault en cumplimiento.
- **MUST** pruebas de restauración programadas (automatizar la restauración periódica; restaurar es operación de plano de control) y medir el tiempo real frente al RTO.
- **MUST** verificar integridad tras restaurar (conteos, checksums, consulta de negocio), no solo "estado completed".
- **SHOULD** Object Lock + versionado en S3 y PITR en DynamoDB y Aurora.
- **SHOULD** denegar por SCP/IAM `ec2:ModifySnapshotAttribute` y `ec2:ModifySnapshotTier` a roles ajenos al backup (el Vault Lock no gobierna llamadas directas a EC2).
- **MUST NOT** asumir que cerrar una cuenta conserva los backups: se borran tras 90 días.

## capacity-and-load-modeling

- **MUST** documentar el modelo de carga: peticiones/s por operación, mezcla de operaciones, tamaño de datos, concurrencia y crecimiento esperado a 6 y 12 meses.
- **MUST** basar los números en telemetría real o en supuestos marcados como tales; nunca en intuición sin etiqueta.
- **MUST** calcular el headroom para el peor caso de fallo soportado: si una AZ cae, las restantes absorben su carga (con 3 AZ cada una dimensionada para 50% del pico, no 33%).
- **MUST** modelar el failover regional: la región superviviente recibe el 100%; si no es capaz, el diseño es un pilot light con degradación explícita (`load-shedding-and-degradation`).
- **MUST** identificar el recurso limitante (CPU, conexiones de BD, IOPS, cuotas de servicio) y la cuota de AWS que se alcanzaría (TODO-VERIFY cuotas).
- **SHOULD** aplicar la ley de Little (concurrencia = tasa x latencia) para dimensionar pools y hilos (`connection-pooling`, `threads-executors-and-pools`).
- **SHOULD** probar carga en entorno aislado con perfil realista (rampa, pico, soak) y criterios de aceptación ligados al SLO.
- **MUST NOT** autoescalar sin límites máximos ni sin considerar las dependencias duras que no escalan (BD).

## change-and-release-management

- **MUST** clasificar el cambio por riesgo (estándar, normal, de emergencia) según tier y radio de impacto (`dependency-mapping-and-blast-radius`).
- **MUST** desplegar de forma progresiva: una celda o región canaria, observación contra SLO y avance por oleadas; nunca todas las regiones a la vez.
- **MUST** tener rollback probado y un plan de reversión para cada cambio; si la migración de datos es irreversible, exigir patrón expand/contract (`schema-migrations`).
- **MUST** automatizar el freno: la promoción se detiene si empeoran los SLIs del canary.
- **MUST** respetar la congelación de cambios activada por el agotamiento del presupuesto de error (`slo-error-budget-policy`), salvo P0 y correcciones de seguridad.
- **MUST** tratar la configuración y los feature flags como cambios con el mismo control que el código.
- **SHOULD** evitar cambios en horas de baja cobertura de guardia y antes de periodos de pico.
- **SHOULD** registrar cada cambio (qué, quién aprueba, cuándo, enlace al commit) para correlacionar con incidentes.
- **MUST NOT** aplicar cambios manuales en consola; todo por IaC/GitOps. La fábrica nunca aplica cambios a AWS (ADR-0004).

## data-replication-matrix

- **MUST** rellenar esta matriz por servicio y revisarla con negocio:

| Almacén | Mecanismo | RPO típico | Nota |
|---|---|---|---|
| Postgres | Aurora Global Database | segundos (asíncrona) | secundaria solo lectura hasta promover |
| Event store | DynamoDB Global Tables | segundos (MREC) | **región de escritura por agregado** |
| Kafka | MSK + replicación entre regiones | minutos | traducción de offsets al conmutar |
| Objetos | S3 CRR + versionado + Object Lock | minutos | RTC si se exige SLA |
| Caché | reconstruir o Global Datastore | n/a | preferir reconstruir |
| Secretos/claves | Vault por región + KMS multi-región | n/a | Transit **no** se comparte |
| Imágenes | ECR replicado | minutos | runtime no depende de Harbor |

- **MUST** en event sourcing con Global Tables fijar **una región de escritura por agregado/tenant**. En modo MREC los conflictos se resuelven por "last writer wins" y las condiciones evalúan contra la versión local, así que el control de concurrencia por versión solo protege dentro de una región.
- **MUST NOT** escribir el mismo agregado en ambas regiones a la vez en MREC.
- **SHOULD** valorar MRSC (consistencia fuerte multi-región, RPO cero) solo si el caso lo exige: exactamente 3 regiones (o 2 + testigo), sin TTL ni transacciones, mayor latencia de escritura. TODO-VERIFY disponibilidad con eu-west-1 y eu-central-1 en uso real.
- **MUST NOT** hacer doble escritura Postgres + NoSQL para "replicar" (4.5): cada agregado tiene una única fuente de verdad.
- **MUST** monitorizar el retraso (ReplicationLatency en MREC, AuroraGlobalDBRPOLag) y alertar frente al RPO del tier.
- **MUST** que los backups con Vault Lock cubran también corrupción lógica, que la replicación propaga.

## dependency-mapping-and-blast-radius

- **MUST** mantener por servicio un fichero `dependencies.yaml` versionado con dependencias de red, datos, identidad, DNS, secretos, CI/CD y terceros.
- **MUST** clasificar cada dependencia como dura (sin ella no hay servicio) o blanda (degradable), con el comportamiento degradado (`load-shedding-and-degradation`).
- **MUST** respetar la regla: un servicio de tier N no puede depender de forma dura de uno de tier inferior en criticidad.
- **MUST** incluir dependencias ocultas: control planes (Argo CD, Vault, Keycloak), emisión de certificados, resolución DNS, registro de imágenes.
- **MUST** estimar el radio de impacto como conjunto de servicios, usuarios y tenants afectados por el fallo de cada dependencia.
- **SHOULD** contrastar el mapa declarado con la telemetría real (trazas, service graph de Tempo) y registrar las diferencias.
- **SHOULD** revisar el mapa en cada cambio de arquitectura y tras cada postmortem.
- **MUST NOT** asumir que una dependencia "regional" de un tercero es independiente de la propia región sin comprobarlo (TODO-VERIFY por proveedor).

## eks-multi-region-and-argo-cd-multicluster

- **MUST** tratar cada región como un clúster EKS independiente (no existe un clúster que abarque regiones); la unidad de fallo es el clúster.
- **MUST** declarar el modelo: activo-activo, activo-pasivo (warm standby) o pilot light, y su coste (`finops-of-resilience`).
- **MUST** definir el clúster como código Terraform parametrizado por región, sin diferencias manuales entre regiones.
- **MUST** usar `ApplicationSet` con el generador `cluster` y labels (`env`, `region`, `tier`) en vez de una `Application` copiada por clúster.
- **MUST** decidir y documentar el modelo de Argo CD: instancia por clúster (blast radius pequeño, más operación) o hub que gestiona clústeres remotos (un punto de fallo y de privilegio).
- **MUST NOT** alojar el único Argo CD en la región que puede fallar; el plano GitOps debe poder reconciliar la región superviviente.
- **MUST NOT** replicar estado de aplicación mediante Argo CD; el estado sigue la matriz de `data-replication-matrix`.
- **SHOULD** desplegar por oleadas (región canaria primero) con `sync-wave`/progressive sync; ver `change-and-release-management`.
- **SHOULD** mantener imágenes en un registro accesible desde ambas regiones (Harbor/ECR con réplica; TODO-VERIFY réplica ECR).

## failover-and-failback-runbooks

- **MUST** que el runbook tenga criterios de decisión, responsable que autoriza, pasos numerados y verificación por paso.
- **MUST** usar solo acciones de plano de datos para conmutar (ARC routing controls, promoción de BD ya aprovisionada) y **MUST NOT** depender de crear recursos nuevos en la región caída.
- **MUST** respetar este orden:
  1. Declarar el desastre y congelar despliegues; frenar escrituras en la primaria si es alcanzable.
  2. Comprobar el lag y elegir la secundaria.
  3. **Promover Aurora Global (failover con pérdida de datos aceptada) y verificar que hay escritor.**
  4. **Solo después**, activar el motor de BD de Vault de la secundaria (rol dinámico) y rotar credenciales.
  5. Escalar EKS/Argo CD de la secundaria a capacidad plena.
  6. Conmutar tráfico (ARC), subiendo el TTL bajo del DNS si aplica.
  7. Verificar SLOs sintéticos y comunicar.
- **MUST** documentar por qué el orden 3 antes de 4: la secundaria Aurora es de solo lectura hasta promoverse y Vault no puede crear roles dinámicos en ella.
- **MUST** definir failback como operación planificada: restaurar topología, sincronizar y hacer *switchover* (RPO 0) en ventana de baja carga, no un segundo failover.
- **MUST** guardar el runbook fuera de la región afectada (repositorio y copia impresa/offline).
- **SHOULD** automatizar los pasos tras una aprobación manual ("botón"); la conmutación automática por alarma suele dar falsos positivos.
- **MUST NOT** declarar RTO hasta cronometrarlo en un ejercicio.

## fault-injection-and-game-days

- **MUST** definir por ejercicio: hipótesis de estado estable, alcance, condición de aborto, responsable, y registro de resultados.
- **MUST** empezar por tabletop: leer el runbook de `failover-and-failback-runbooks` con el equipo, cronometrar decisiones y anotar huecos.
- **SHOULD** progresar: local (Toxiproxy/Chaos Mesh) -> preproducción -> producción acotada, solo cuando exista entorno real.
- **MUST** incluir escenarios: pérdida de AZ, latencia/caída de dependencia, región primaria no disponible, lag de replicación alto, credenciales de BD caducadas tras failover (orden Aurora-Vault), registro de imágenes inaccesible.
- **MUST** tratar los experimentos AWS FIS (p. ej. aislar una réplica de Global Tables) como diseño documentado "no ejecutado"; el servicio es una opción de AWS, cuyas acciones concretas son TODO-VERIFY.
- **MUST** cerrar cada ejercicio con acciones asignadas y fecha; **MUST NOT** repetir el mismo ejercicio sin revisar las acciones previas.
- **SHOULD** ejercicios sin culpa; el resultado alimenta `incident-management-and-postmortems`.
- **MUST NOT** ejecutar chaos sin observabilidad ni plan de retorno.

## finops

- **MUST** definir una política de etiquetas obligatorias (`service`, `env`, `owner`, `cost-center`, `tier`) aplicada por Terraform (`default_tags`) y activarlas como etiquetas de asignación de costes (TODO-VERIFY activación).
- **MUST** declarar presupuestos como código (AWS Budgets) por entorno/servicio con umbrales de aviso (p. ej. 50/80/100% real y 100% previsto) y destinatario.
- **MUST** declarar monitores y suscripciones de Cost Anomaly Detection; las alertas pueden ir a email o a un tema SNS. La detección no es inmediata: usa datos de Cost Explorer con hasta 24 h de retraso.
- **MUST** medir un coste unitario por negocio (coste por pedido, por tenant, por 1000 peticiones) y seguirlo como métrica junto al SLO.
- **MUST** revisar rightsizing con datos de utilización de al menos 14-30 días antes de reducir; nunca por intuición, y respetando el headroom de `capacity-and-load-modeling`.
- **SHOULD** apagar entornos efímeros fuera de horario y con TTL (`ephemeral-environments`).
- **SHOULD** revisar mensualmente los 5 mayores conceptos de coste y los recursos huérfanos (volúmenes, IP elásticas, snapshots).
- **MUST NOT** comprometer Savings Plans/instancias reservadas sin carga base estable demostrada y aprobación humana.
- **MUST NOT** recortar coste a costa de backups, observabilidad mínima o headroom del tier sin ADR.

## finops-of-resilience

- **MUST** calcular, para cada tier, el coste de la estrategia (cómputo en espera, réplicas de datos, transferencia entre regiones, backups, herramientas) frente al coste de indisponibilidad (ingresos perdidos por hora x RTO esperado + penalizaciones).
- **MUST** elegir la estrategia más barata que cumpla el RPO/RTO del tier, no la más robusta disponible (`tier-model-and-rpo-rto`).
- **MUST** separar en el modelo costes fijos (infra en espera) de variables (replicación proporcional al tráfico).
- **MUST** etiquetar con `tier`, `service` y `dr-role` todos los recursos de resiliencia para atribuir su coste (`finops`).
- **MUST NOT** aplicar activo-activo a tiers 3-4 sin un ADR que lo justifique.
- **SHOULD** apagar o reducir el entorno de warm standby de menor tier fuera de ventana si el RTO lo permite.
- **SHOULD** incluir en el presupuesto el coste de ensayar: game days, restore tests y entornos temporales.
- **SHOULD** revisar el modelo cada trimestre y tras cada cambio de tier.

## incident-management-and-postmortems

- **MUST** definir severidades (SEV1-SEV4) ligadas al impacto en SLO y tier, con tiempos de respuesta y quién declara.
- **MUST** asignar roles al declarar: comandante de incidente, comunicaciones y operaciones; el comandante coordina, no depura.
- **MUST** mantener un canal único y una línea de tiempo con marcas horarias en UTC.
- **MUST** comunicar a interesados con una cadencia fija y a la página de estado (`status-page-and-comms`).
- **MUST** priorizar mitigar (rollback, failover, apagado de feature) sobre diagnosticar la causa raíz.
- **MUST** escribir un postmortem sin culpas para SEV1/SEV2 y cuando un incidente consuma presupuesto de error alto (`slo-error-budget-policy`), en un plazo definido (p. ej. 5 días laborables).
- **MUST** que cada acción del postmortem tenga dueño, fecha y ticket; las acciones sin dueño se consideran no aceptadas.
- **SHOULD** registrar detección, mitigación y recuperación (TTD/TTM/TTR) para tendencias.
- **MUST NOT** citar nombres para atribuir culpa ni incluir datos personales o secretos en el postmortem.

## istio-multicluster-tradeoffs

- **MUST** justificar por escrito por qué hace falta una malla compartida; la opción por defecto es una malla por región.
- **MUST** elegir el modelo de plano de control: multi-primary (un control plane por clúster, fallo acotado, configuración a sincronizar) o primary-remote (más simple, dependencia centralizada).
- **MUST** declarar la topología de red: red única (IPs sin solapamiento, conectividad directa) o multi-red (gateways este-oeste, permite rangos solapados).
- **MUST** asegurar que la misma configuración (`VirtualService`, `AuthorizationPolicy`) se aplica a todos los clústeres vía GitOps (`eks-multi-region-and-argo-cd-multicluster`); la deriva rompe el failover.
- **MUST** definir identidad y raíz de confianza compartida (CA común o intermedia por clúster) y su rotación.
- **MUST NOT** depender del control plane de un único clúster para que el tráfico de la región superviviente siga funcionando (`static-stability-and-cell-architecture`).
- **SHOULD** usar balanceo por localidad con `outlierDetection` para failover automático; medir el tráfico entre regiones (coste de transferencia, `finops-of-resilience`).
- **SHOULD** limitar el alcance de endpoints visibles entre clústeres a los servicios que lo necesitan.
- **SHOULD** valorar el modo ambient/sidecar según la versión adoptada (TODO-VERIFY estado de multicluster en ambient).

## load-shedding-and-degradation

- **MUST** clasificar el tráfico por criticidad (p. ej. pagos > consulta > informes) y descartar primero lo menos crítico.
- **MUST** limitar la concurrencia por servicio y rechazar de forma temprana con `503` + `Retry-After` antes de agotar hilos o memoria.
- **MUST** definir niveles de degradación documentados por servicio (nivel 0 normal, 1 sin recomendaciones, 2 solo lectura, 3 solo tráfico crítico) y su disparador medible.
- **MUST** que los clientes usen timeouts, reintentos con backoff exponencial y jitter, y un presupuesto de reintentos; los reintentos sin límite amplifican la caída (`http-clients-and-timeouts`, `resilience`).
- **MUST** exponer métricas de descarte (cuántas peticiones, de qué clase) y alertar sobre ellas.
- **SHOULD** preferir degradar (caché obsoleta, valor por defecto) a fallar cuando la dependencia es blanda (`dependency-mapping-and-blast-radius`).
- **SHOULD** activar la degradación de forma automática por señal de saturación (latencia de cola, cola de peticiones) y permitir un interruptor manual.
- **MUST NOT** descartar peticiones no idempotentes tras haberlas procesado a medias; rechazar antes de empezar (`idempotency-keys`).
- **MUST** ensayar los modos degradados en un game day en papel (`fault-injection-and-game-days`).

## multi-az-patterns

- **MUST** repartir nodos de EKS en 3 AZ y usar `topologySpreadConstraints` por `topology.kubernetes.io/zone` en cada Deployment con más de 1 réplica.
- **MUST** definir un `PodDisruptionBudget` por servicio con `minAvailable` o `maxUnavailable` coherente con las réplicas.
- **MUST** usar Aurora Multi-AZ (instancia lectora en otra AZ), MSK en 3 AZ con `min.insync.replicas` >= 2 y `replication.factor` 3, ElastiCache Multi-AZ, Vault Raft con 3 nodos en 3 AZ.
- **MUST** que las réplicas de un servicio no superen la capacidad que queda al perder una AZ (N+1 por AZ): con 3 AZ, dimensionar al 150 % de la carga.
- **SHOULD** usar zonal shift de ARC para sacar una AZ degradada (ver `application-recovery-controller-and-health-checks`).
- **MUST NOT** fijar `nodeSelector`/`nodeAffinity` a una AZ concreta salvo volúmenes EBS zonales justificados.
- **MUST NOT** usar tráfico entre AZ innecesario sin medir su coste (ver `finops-of-resilience`).

## multi-region-patterns

- **MUST** desplegar un clúster EKS gemelo en la secundaria con Terraform y Argo CD (mismo repo GitOps, overlay por región), a escala reducida pero funcional (warm standby).
- **MUST** un **clúster Vault independiente por región** (Raft 3 AZ cada uno). El material de claves de Transit no se comparte entre ellos.
- **MUST** cifrar con claves multi-región de KMS (cifrado de sobre) los datos que deban leerse desde ambas regiones; **MUST NOT** usar Vault Transit para eso.
- **MUST** desplegar desde **ECR con replicación cross-region nativa**; el runtime no depende de Harbor ni del repositorio de artefactos para arrancar.
- **MUST** que CI/CD y el estado de Terraform sean accesibles aunque la región primaria caiga (estado/bucket y runners en la secundaria o fuera del dominio de fallo).
- **MUST** fijar la región de escritura por agregado en datos con Global Tables (ver `data-replication-matrix`).
- **MUST NOT** asumir replicación de Vault (función de pago): es variante opcional, no el diseño base (D16).
- **SHOULD** mantener cuotas de servicio en la secundaria suficientes para escalar a producción completa.
- **SHOULD** que Keycloak use la BD de Aurora Global; asumir reinicio de sesiones en failover.

## resilience-hub-assessments

- **MUST** expresar la política de resiliencia de cada tier (RTO/RPO por fallo de aplicación, infraestructura, AZ y región) en un fichero versionado del proyecto, coherente con `tier-model-and-rpo-rto`.
- **MUST** tratar el resultado como estimación basada en configuración, no como medición; **MUST NOT** usarla para afirmar que un RTO "está probado".
- **SHOULD** definir la aplicación por pila Terraform/tags para que el inventario sea reproducible. TODO-VERIFY orígenes de recursos soportados.
- **SHOULD** convertir cada recomendación en issue con prioridad y dueño, o en riesgo aceptado documentado.
- **SHOULD** repetir la evaluación tras cambios relevantes y antes de cada revisión anual de tier.
- **MUST** validar que el coste de las recomendaciones cabe en el presupuesto (`finops-of-resilience`).
- **MUST NOT** aplicar recomendaciones sin pasar por PR y revisión de IaC.

## slo-error-budget-policy

- **MUST** definir por servicio SLIs desde la perspectiva del usuario (disponibilidad, latencia, frescura) con ventana móvil (p. ej. 28 días).
- **MUST** fijar el SLO por debajo del 100% y derivarlo del tier; el presupuesto de error es `1 - SLO`.
- **MUST** tener una política escrita y firmada por producto e ingeniería que diga qué ocurre al agotar el presupuesto.
- **MUST** definir como mínimo: congelar cambios no críticos (salvo P0 y correcciones de seguridad) hasta recuperar el SLO, prioridad a trabajo de fiabilidad y mecanismo de escalado para discrepancias.
- **MUST** alertar por velocidad de consumo (burn rate) en varias ventanas, no por umbral de error instantáneo.
- **SHOULD** exigir postmortem cuando un solo incidente consuma un porcentaje alto del presupuesto (el ejemplo de Google usa 20%; ajustar).
- **SHOULD** excluir del cómputo tráfico fuera de alcance (pruebas de carga, pentest) y documentarlo.
- **MUST NOT** usar el SLO como arma entre equipos ni cambiarlo tras un incumplimiento sin revisión formal.

## static-stability-and-cell-architecture

- **MUST** que la conmutación solo requiera acciones de plano de datos: la capacidad que absorbe el tráfico inicial ya está aprovisionada (estabilidad estática).
- **MUST** dimensionar la secundaria de warm standby para la carga inicial esperada tras el failover y documentar el resto de rampa (HPA, Karpenter) como dependencia de plano de control, con cuotas reservadas.
- **SHOULD** tier 0: capacidad plena en ambas regiones (hot standby o activo-activo).
- **SHOULD** dividir servicios críticos en celdas (cada una con su propio conjunto de tenants, colas y datos) con un enrutador fino y estable; **MUST NOT** compartir estado entre celdas.
- **MUST** acotar el radio de impacto: despliegues progresivos celda a celda (ver `change-and-release-management`).
- **MUST NOT** colocar en el camino crítico de recuperación servicios que viven solo en la región afectada (registro, config, secretos, state).
- **SHOULD** medir el "tamaño máximo de celda" y limitar tenants por celda.

## tier-model-and-rpo-rto

- **MUST** declarar un tier por servicio en un fichero `resilience.yaml` del proyecto (tier, RPO, RTO, aprobador de negocio).
- **MUST** usar **Tier 1 (warm standby)** como defecto para servicios de cara a cliente salvo decisión documentada.
- **MUST** tratar los valores de la tabla como "valores de partida, a validar con negocio", no como compromisos.
- **MUST** derivar la infraestructura del tier: el tier activa módulos Terraform concretos, no al revés.
- **MUST NOT** declarar Tier 0 sin haber resuelto la región de escritura por agregado y la ruta de datos multi-región (ver `data-replication-matrix`).
- **SHOULD** distinguir RPO/RTO de fallo de AZ (casi cero) del de región (el tier).
- **SHOULD** revisar el tier cada año o tras un incidente mayor.
- **MUST NOT** prometer RTO/RPO sin un ejercicio que lo respalde (`fault-injection-and-game-days`).
