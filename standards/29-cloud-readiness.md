# Estándares · 29-cloud-readiness

> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.

## cost-estimation

- **MUST** presentar toda cifra como estimación de diseño con supuestos explícitos (región, horas/mes, tráfico, almacenamiento), nunca como coste real.
- **MUST** estimar desde el código o HCL sin credenciales AWS. Infracost admite analizar un directorio Terraform; TODO-VERIFY modo sin plan, API key gratuita y licencia vigente, porque D16 prohíbe licencias de pago por defecto. Alternativa: tabla propia con precios oficiales fechados.
- **MUST** citar la fuente y fecha de cada precio unitario; los precios se verifican en la página oficial de AWS, no se memorizan (TODO-VERIFY).
- **MUST** reflejar el multiplicador del tier: 0 activo-activo (muy alto, aprox. 2x), 1 warm standby (alto, defecto), 2 pilot light (medio), 3 backup y restauración (bajo).
- **MUST** incluir las dos regiones del diseño (eu-west-1 primaria, eu-central-1 secundaria, D6) y la transferencia entre regiones en tiers 0 a 2.
- **SHOULD** dar rango (mínimo/esperado/pico) en vez de cifra única.
- **SHOULD** comparar el coste con el RTO/RPO del tier para que el negocio decida.
- **MUST NOT** afirmar que el coste "se verificó" ni usar la estimación como compromiso presupuestario.

## dr-tabletop-exercises

- **MUST** partir de `catalog/resilience-tiers.yaml`: el tier por defecto es 1 (warm standby, RPO aprox. minutos, RTO menor de 1 h). Los valores son de partida y los confirma negocio.
- **MUST** definir para cada ejercicio: escenario, tier, participantes con rol (facilitador, escriba, responsables de plataforma, datos y seguridad), supuestos y criterios de éxito.
- **MUST** recorrer, por componente, la acción de plano de datos que conmuta (promoción de Aurora Global Database, región de escritura de Global Tables, replicación de MSK y S3, Application Recovery Controller), según el principio de estabilidad estática.
- **MUST** incluir escenarios incómodos: la región caída contiene CI/CD o el estado de IaC; Vault independiente por región; reinicio de sesión de Keycloak.
- **MUST** registrar hallazgos con dueño y fecha, y convertirlos en tareas o ADR.
- **MUST** etiquetar el resultado como "simulacro documental; no verificado en real" (ver `maturity-labels`).
- **SHOULD** repetir el ejercicio al cambiar de tier o de topología, y al menos una vez al año (convención sugerida, a confirmar).
- **MUST NOT** presentar el tabletop como prueba de que el RTO/RPO se cumple.

## honest-claims-policy

- **MUST** usar la fórmula "preparado para AWS, no verificado en real" cuando se hable del estado de la infraestructura.
- **MUST NOT** afirmar que algo esté listo para producción en AWS, ni probado, testado, verificado, validado o desplegado en AWS real, ni que "funciona en AWS real". Son los patrones que rechaza el validador.
- **MUST** reflejar que la fábrica nunca despliega (ADR-0004) ni hace `terraform plan` contra una cuenta (ADR-0037); el techo es "validada estáticamente".
- **MUST** que una mención de esas frases como ejemplo malo vaya precedida de negación o prohibición ("nunca", "no está", "prohibido afirmar"); es lo que el validador admite. Preferir describir el patrón sin repetirlo.
- **MUST** usar el marcador de exclusión del validador solo al citar un mal ejemplo, y con motivo en la misma línea.
- **MUST** tratar normativa y legal como borrador por confirmar con fuente oficial y fecha.
- **SHOULD** sustituir adjetivos de calidad por evidencia: qué peldaño de `static-verification-ladder` se superó y cuándo.
- **MUST NOT** relajar el validador o el hook para que pase un texto; corregir el texto.

## maturity-labels

- **MUST** que cada directorio con ficheros `.tf` tenga un `README.md` con una etiqueta de madurez.
- **MUST** usar solo estos niveles, de menor a mayor: `borrador` (sin ejecutar nada), `validada estáticamente` (superó `static-verification-ladder`), `simulada en local` (comportamiento reproducible comprobado en kind, con límites de `local-parity-matrix`).
- **MUST** que el techo para infraestructura AWS sea `validada estáticamente`; no existe nivel superior en la fábrica (ADR-0004).
- **MUST** acompañar el nivel con la fórmula "preparado para AWS, no verificado en real".
- **MUST** indicar fecha y herramientas con versión en la etiqueta, para que caduque de forma visible.
- **SHOULD** degradar la etiqueta a `borrador` si cambia el código y no se repite la escalera.
- **MUST NOT** inventar niveles ("certificada", "auditada", "lista") ni usar la etiqueta para sugerir despliegue real.
- **MUST NOT** copiar la etiqueta de otro módulo sin ejecutar la escalera en este.

## parity-matrix-maintenance

- **MUST** que toda fila de `catalog/parity-matrix.yaml` tenga `aws`, `local` (o `null` si no hay equivalente) y `not_reproduced` no vacío.
- **MUST** actualizar en el mismo cambio los skills que citan la fila (por ejemplo `aws-emulation`, `local-profiles`, `local-parity-matrix`) y `last_reviewed`.
- **MUST** que un servicio sin equivalente local tenga `local: null` y `not_reproduced` explícito, nunca eliminarse de la matriz.
- **MUST** dejar `TODO-VERIFY` donde el estado de un emulador no esté comprobado en documentación oficial (caso Streams de DynamoDB en LocalStack).
- **MUST** respetar ADR-0034 (kind por defecto, k3d alternativa) al editar la fila de EKS.
- **SHOULD** revisar la matriz al cambiar versión de un operador (CloudNativePG, Strimzi) o la política de licencias de un emulador (LocalStack, D16).
- **SHOULD** registrar el cambio en un ADR si altera una decisión cerrada D1 a D27.
- **MUST NOT** cambiar `local` a algo con licencia de pago por defecto.
- **MUST NOT** borrar un `not_reproduced` para "limpiar" la matriz.

## static-verification-ladder

- **MUST** recorrer los peldaños en orden y detenerse en el primero que falle:
  1. `terraform fmt -check` y `terraform validate` (con `terraform init -backend=false`).
  2. `tflint` (reglas del provider AWS, TODO-VERIFY plugin y versión).
  3. Checkov o Trivy en modo config sobre el directorio (`checkov -d .`, `trivy config .`), más las reglas propias de `policies/iac-checks/`.
  4. OPA/Conftest con Rego de `policies/opa-conftest/` sobre HCL (`conftest test --parser hcl2`, TODO-VERIFY flag) o sobre JSON de plan generado con providers simulados.
  5. `terraform test` con `mock_provider` (TODO-VERIFY versión mínima de Terraform) para comprobar lógica de módulos sin credenciales.
- **MUST** que ningún peldaño requiera credenciales AWS ni red hacia AWS; si lo pide, el peldaño no pertenece a la escalera.
- **MUST NOT** ejecutar `terraform plan` ni `apply` contra AWS. Un plan solo es válido con providers simulados o salida sintética.
- **MUST** reportar el resultado con la etiqueta de `maturity-labels`: llegar al peldaño 5 significa "validada estáticamente", nunca más.
- **SHOULD** versionar las excepciones de Checkov/Trivy con justificación y fecha de revisión.
- **SHOULD** ejecutar la escalera en CI y en pre-commit local (peldaños 1 a 3).
