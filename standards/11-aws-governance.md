# Estándares · 11-aws-governance

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## break-glass-and-jit-access

- **MUST** que el acceso privilegiado normal sea JIT: permission set elevado asignado por tiempo limitado con aprobación y motivo (ticket).
- **MUST** tener un mecanismo break-glass para cuando el IdP o Identity Center no estén disponibles: roles IAM en cuentas clave asumibles por un número mínimo de principales, con MFA hardware.
- **MUST** que cualquier uso de break-glass dispare alerta inmediata (EventBridge sobre `AssumeRole`/`ConsoleLogin` del rol) a un canal con respuesta humana.
- **MUST** custodiar credenciales break-glass offline con doble control (dos personas) y rotarlas tras cada uso.
- **MUST** probar el procedimiento al menos cada 6 meses y registrar el resultado.
- **SHOULD** limitar la sesión (≤ 1 h) y acotar con SCP/permission boundary lo que el rol puede hacer.
- **MUST NOT** usar el usuario root para operar; reservarlo para tareas que solo root puede hacer, con MFA y alerta.
- **MUST NOT** guardar las credenciales de emergencia en el repo ni en un gestor accesible vía el mismo IdP caído.

## compliance-as-code

- **MUST** que cada control tenga: id, requisito de origen, capa (CI/SCP/Config), responsable y modo de evidencia.
- **MUST** ejecutar en CI, sobre el plan de Terraform, Checkov y Conftest/OPA; el fallo bloquea el merge.
- **MUST** reflejar los controles detectivos como Config rules o conformance packs gestionados por Terraform.
- **MUST** registrar excepciones en fichero versionado con motivo, dueño y fecha de caducidad; nunca `#checkov:skip` sin referencia.
- **SHOULD** preferir checks nativos de Checkov antes de escribir custom; los custom van en `policies/iac-checks/`.
- **SHOULD** generar evidencias (informe de CI, estado de Config) como artefactos retenibles.
- **MUST NOT** declarar "cumple" un marco normativo: la fábrica solo ofrece controles técnicos; la conformidad la decide una revisión humana externa.
- **MUST NOT** afirmar que un control funciona en AWS real: estado máximo "validado estáticamente".

## control-tower-and-account-factory

- **MUST** decidir y registrar en un ADR del proyecto: Control Tower + Account Factory for Terraform (AFT), o Organizations + Terraform propio. Ambos son válidos.
- **MUST** que el alta de cuenta sea código revisado (PR), nunca consola.
- **MUST** fijar la home region de la landing zone en eu-west-1 y gobernar eu-central-1 como región secundaria (D6); la home region no se puede cambiar después sin rehacer la landing zone (TODO-VERIFY).
- **MUST** aplicar una línea base a toda cuenta nueva: CloudTrail org, Config, roles de acceso vía Identity Center, tags obligatorios y presupuesto.
- **SHOULD** versionar la personalización de cuentas (baseline) como módulo Terraform con tests estáticos.
- **SHOULD** mantener la lista de regiones gobernadas explícita, no "todas".
- **MUST NOT** crear usuarios IAM de larga duración como parte del alta.
- **MUST NOT** asumir que Control Tower existe en local: no se reproduce; los equivalentes locales son solo contratos de módulo.

## identity-center-sso

- **MUST** dar acceso humano solo vía Identity Center con credenciales temporales; cero usuarios IAM con claves de larga duración.
- **MUST** asignar permission sets a grupos, nunca a usuarios individuales.
- **MUST** federar el IdP corporativo (Keycloak como IdP externo vía SAML/SCIM, TODO-VERIFY soporte SCIM) y exigir MFA en el IdP.
- **MUST** limitar la duración de sesión (por defecto ≤ 8 h; admin ≤ 1 h).
- **MUST** separar permission sets: `ReadOnly`, `Developer`, `Deployer` (CI), `PlatformAdmin`, `SecurityAudit`.
- **SHOULD** gestionar grupos y asignaciones por Terraform.
- **SHOULD** ubicar la instancia en eu-west-1 (región primaria, D6); la región de la instancia es difícil de cambiar (TODO-VERIFY).
- **MUST NOT** conceder `AdministratorAccess` permanente a nadie en prod; ver `break-glass-and-jit-access`.

## kms-multi-region-keys

- **MUST** usar CMK gestionadas por el cliente (no claves `aws/*`) para datos sensibles y logs de seguridad.
- **MUST** separar claves por dominio de datos y entorno (`orders-prod-data`, `org-trail`), no una clave global.
- **MUST** activar rotación automática en claves simétricas.
- **MUST** usar claves multi-región (réplica en eu-central-1) solo donde la recuperación entre regiones lo requiera (D6); la réplica comparte material pero tiene key policy propia.
- **MUST** escribir la key policy con mínimo privilegio, separando administradores de usuarios de la clave; sin `"Principal": "*"` sin condición.
- **MUST** denegar `ScheduleKeyDeletion` por SCP y exigir ventana de espera máxima.
- **SHOULD** usar alias (`alias/orders-prod-data`) y nunca ARNs de clave embebidos en código.
- **SHOULD** usar grants o condiciones `kms:ViaService` para acotar el uso.
- **MUST NOT** usar claves multi-región por defecto: amplían el radio de impacto.

## log-archive-and-audit-account

- **MUST** separar `log-archive` (solo almacenamiento) de `audit` (herramientas de seguridad y consulta de solo lectura).
- **MUST** activar en los buckets: versionado, Block Public Access, cifrado SSE-KMS y S3 Object Lock en modo compliance o governance según política (TODO-VERIFY requisitos legales).
- **MUST** definir retención explícita (p. ej. 365 días en caliente y archivado después; plazo legal por confirmar con fuente oficial) con lifecycle.
- **MUST** replicar a un bucket en eu-central-1 (secundaria, D6) si el log es evidencia.
- **MUST** restringir con política de bucket: escritura solo desde servicios de la organización (`aws:PrincipalOrgID`), borrado denegado.
- **SHOULD** dar a `audit` acceso de lectura mediante rol, nunca claves.
- **MUST NOT** permitir a roles de workload leer el bucket de logs de seguridad.
- **MUST NOT** guardar datos personales en claro en logs.

## org-cloudtrail-config-securityhub-guardduty

- **MUST** crear un trail de organización multi-región, con validación de integridad de ficheros, entregado al bucket de `log-archive`.
- **MUST** habilitar AWS Config con agregador en la cuenta `audit` y registrar recursos en eu-west-1 y eu-central-1 (D6).
- **MUST** habilitar GuardDuty y Security Hub con administrador delegado en la cuenta `audit` y auto-enable para cuentas nuevas.
- **MUST** cifrar trail y entregas con CMK (ver `kms-multi-region-keys`).
- **MUST** definir el estándar de Security Hub adoptado (p. ej. AWS Foundational Security Best Practices) y registrar excepciones con caducidad.
- **SHOULD** enrutar hallazgos HIGH/CRITICAL a un canal de alerta con propietario.
- **SHOULD** habilitar data events solo donde aporte (coste); documentar la decisión.
- **MUST NOT** gestionar estos servicios desde la cuenta de management más allá del alta de la delegación.
- **MUST NOT** permitir que una cuenta miembro desactive el trail (SCP, ver `scp-guardrails`).

## organization-and-ou-design

- **MUST** usar cuentas distintas como frontera de aislamiento: una por entorno (`dev`, `staging`, `prod`) y por dominio de carga cuando el blast radius lo justifique.
- **MUST** tener cuentas dedicadas de gestión (management, sin cargas), `log-archive` y `audit` (ver `log-archive-and-audit-account`).
- **MUST** organizar OUs por función de política, no por organigrama: `Security`, `Infrastructure`, `Workloads/Prod`, `Workloads/NonProd`, `Sandbox`, `Suspended`.
- **MUST** parametrizar regiones: eu-west-1 primaria y eu-central-1 secundaria (D6), sin literales en módulos.
- **MUST NOT** ejecutar cargas de trabajo en la cuenta de management.
- **SHOULD** limitar la profundidad de OUs (≤ 3 niveles) para que las SCP sean razonables.
- **SHOULD** usar emails de cuenta como alias de grupo (`aws+prod-orders@example.com`), nunca personales.
- **SHOULD** mover cuentas cerradas a la OU `Suspended` con SCP de denegación total.

## regions-and-data-residency

- **MUST** parametrizar regiones: `primary_region = "eu-west-1"` y `secondary_region = "eu-central-1"` como variables y aliases de provider; ningún literal en módulos.
- **MUST** mantener datos personales y de negocio solo en esas dos regiones; denegar el resto por SCP (ver `scp-guardrails`).
- **MUST** decidir por dato si se replica a la secundaria; la replicación es explícita, nunca por defecto.
- **MUST** respetar la regla de datos: sin doble escritura Postgres+NoSQL; replicar cada almacén con su mecanismo nativo.
- **MUST** verificar antes de diseñar que cada servicio existe en ambas regiones (TODO-VERIFY, pendiente de ADR-0006).
- **SHOULD** tratar servicios globales (IAM, Route 53, CloudFront) como excepciones documentadas; sus datos de control pueden salir de la UE (TODO-VERIFY).
- **SHOULD** documentar el RPO/RTO objetivo por servicio con la región secundaria.
- **MUST NOT** afirmar cumplimiento RGPD por usar regiones UE: es borrador por confirmar con fuente oficial y asesoría legal.
- **MUST NOT** copiar backups o logs con datos personales fuera de las dos regiones.

## scp-guardrails

- **MUST** usar estrategia "deny list": mantener `FullAWSAccess` y añadir denegaciones concretas.
- **MUST** denegar acciones fuera de eu-west-1 y eu-central-1 (D6) con `aws:RequestedRegion`, exceptuando servicios globales (IAM, Organizations, Route 53, CloudFront, etc.; lista por validar, TODO-VERIFY).
- **MUST** denegar desactivar o borrar CloudTrail, Config, GuardDuty y Security Hub de la organización.
- **MUST** denegar uso del usuario root en cuentas miembro y la creación de access keys.
- **MUST** denegar `kms:ScheduleKeyDeletion` y `kms:DisableKey` salvo rol de plataforma.
- **MUST** probar cada SCP en una OU `Sandbox` antes de adjuntarla a `Workloads`.
- **SHOULD** versionar SCP en ficheros JSON con `Sid` descriptivo y tamaño < límite de 5120 caracteres (TODO-VERIFY).
- **MUST NOT** adjuntar SCP experimentales a la raíz de la organización.
- **MUST NOT** olvidar que las SCP no afectan a la cuenta de management.

## tagging-cost-allocation-budgets

- **MUST** definir un conjunto mínimo de tags: `project`, `environment`, `owner`, `cost-center`, `data-classification`.
- **MUST** aplicarlos con `default_tags` del provider, no recurso a recurso.
- **MUST** activar los tags como cost allocation tags en la cuenta de facturación (la activación no es retroactiva, TODO-VERIFY).
- **MUST** crear un AWS Budget por cuenta con avisos al 50/80/100 % y al previsto, con destinatario real (alias de grupo).
- **SHOULD** usar un tag policy de Organizations para fijar claves y valores permitidos.
- **SHOULD** añadir detección de anomalías de coste.
- **MUST NOT** meter datos personales ni secretos en tags.
- **MUST NOT** depender de tags para autorización sin entender que son editables (usar ABAC solo con control de `TagResource`).
