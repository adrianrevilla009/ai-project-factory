# iac-checks

La **especificación** de las comprobaciones de infraestructura como código que piden las skills y que todavía no están implementadas: qué debe detectar cada una y de qué skill sale. Esta fábrica solo guía, así que cada proyecto generado implementa las que le apliquen, con la herramienta que adopte (Checkov, Trivy en modo configuración u OPA/Conftest).

## Cómo usar esta lista
1. **Primero lo nativo:** antes de escribir un check propio, comprueba si la herramienta ya lo cubre (por ejemplo, Checkov trae comprobaciones de rotación de claves KMS o de cifrado de CloudTrail).
2. **Solo lo que falte:** un check propio se justifica cuando el nativo no cubre la regla de la skill.
3. **Con pruebas:** cada check lleva un caso que debe fallar y otro que debe pasar.

Skills relacionadas: `compliance-as-code` y `static-verification-ladder`.

## Checks solicitados por las skills
| Skill | Qué debe detectar |
|---|---|
| `application-recovery-controller-and-health-checks` | registros de failover con health check |
| `build-and-deploy` | bucket del frontend sin acceso público y distribución sin HTTPS obligatorio |
| `cloud-iam-least-privilege` | comodín en acción/recurso |
| `control-tower-and-account-factory` | `aws_iam_user`/`aws_iam_access_key` prohibidos |
| `cross-region-connectivity-and-cost` | alerta ante peering o rutas inter-región no inventariadas |
| `data-lake-and-lakehouse` | bucket S3 sin cifrado o con acceso público |
| `data-platform-cost` | buckets de datos sin ciclo de vida o recursos sin tag de dominio |
| `dns-route53-private-and-hybrid` | no `domain_name = "."` en reglas FORWARD |
| `document-management` | bucket S3 sin acceso público y con cifrado |
| `encryption-standards` | recursos de datos sin cifrado en reposo |
| `envelope-encryption-and-kms` | claves KMS sin rotación o sin réplicas multi-región definidas cuando se exigen |
| `finops` | recursos sin tags obligatorios |
| `finops-of-resilience` | exigir tags `tier` y `dr-role` |
| `flow-logs-and-network-observability` | destino en cuenta de archivo, no en la cuenta de carga |
| `hybrid-identity-and-networking` | reglas de red hacia on-premise abiertas a todo el rango |
| `identity-center-sso` | `aws_iam_user`, `aws_iam_access_key`, `principal_type = "USER"` |
| `kms-multi-region-keys` | rotación de claves KMS y política sin principal comodín (nativos: CKV_AWS_7 y CKV_AWS_33) |
| `log-archive-and-audit-account` | bucket de logs sin versionado, sin bloqueo de acceso público o sin KMS (comprobaciones nativas) |
| `multi-region-patterns` | ECR con replicación |
| `org-cloudtrail-config-securityhub-guardduty` | `aws_cloudtrail` sin `is_multi_region_trail`, sin validación de integridad o sin KMS (nativos: CKV_AWS_35, 36 y 67) |
| `organization-and-ou-design` | `aws_instance`/`aws_eks_cluster` en cuenta de management |
| `private-endpoints-and-egress-control` | endpoints requeridos y política no `"*"` |
| `rabbitmq-sqs` | SQS sin cifrado / sin DLQ |
| `retention-and-cleanup` | repositorio ECR sin `aws_ecr_lifecycle_policy` |
| `scp-guardrails` | SCP con `Action: "*"` y `Resource: "*"` en Deny |
| `tagging-cost-allocation-budgets` | provider sin `default_tags` |
| `transit-gateway-hub-and-spoke` | asociación/propagación por defecto desactivadas |
| `vpc-multi-az-layers` | un NAT por AZ |

## Cómo se implementa un check propio (convención)
- **Checkov:** un check en Python o un check de grafo en YAML, con un id propio que no choque con los nativos, y una carpeta de ejemplos `pass` y `fail`.
- **Conftest (Rego):** una política sobre el JSON de `terraform show -json` o sobre HCL, con sus casos de prueba.
- **Dónde vive:** en el repositorio del proyecto generado, no aquí. Esta lista es la especificación de partida.
