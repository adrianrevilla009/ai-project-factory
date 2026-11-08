---
name: aws-emulation
description: "Usar al decidir cómo emular servicios AWS en local (DynamoDB Local, MinIO, LocalStack) y al documentar sus límites; no sustituye a AWS."
metadata:
  block: "28-local-kubernetes"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Emulación de AWS en local y sus límites

## Cuándo aplicar y cuándo no
- Aplica al elegir qué contenedor o emulador sustituye a un servicio AWS en el clúster local (kind, ADR-0034) y al escribir su configuración.
- No aplica a tests de integración con Testcontainers (siguen siendo necesarios) ni a cualquier verificación contra una cuenta AWS real: la fábrica nunca despliega (ADR-0004).

## Reglas
- **MUST** preferir el emulador oficial o de código abierto sin cuenta: DynamoDB Local (`amazon/dynamodb-local`) para DynamoDB, MinIO para S3, Redis para ElastiCache, Strimzi para MSK.
- **MUST** tratar LocalStack como opcional: hoy exige Auth Token (https://docs.localstack.cloud/aws/getting-started/auth-token/, 2026-11-07), lo que choca con D16. Comprobar el plan gratuito vigente antes de adoptarlo.
- **MUST** acceder a los emuladores por configuración de endpoint (`endpoint-override`), nunca con ramas `if (local)` en el código de dominio.
- **MUST** que las credenciales del emulador sean de ejemplo (`example`/`changeme`) y vivan solo en el perfil local.
- **MUST** listar en el README del perfil qué NO se reproduce (ver `local-parity-matrix`): Global Tables fiables, throttling, backups y consistencia eventual en DynamoDB; replicación y Object Lock completo en S3; Multi-AZ en Redis.
- **SHOULD** probar contratos (esquemas, claves, condiciones de escritura) en local y dejar rendimiento, límites de cuota y resiliencia como "no verificado".
- **MUST NOT** afirmar que un comportamiento está comprobado en AWS por haber pasado contra un emulador.
- **MUST NOT** emular IAM de AWS: en local la autorización es RBAC de Kubernetes.

## Por qué
Un emulador valida que el código habla el protocolo correcto, no que el servicio real se comporte igual. Declarar los límites evita falsa confianza; usar solo emuladores sin licencia mantiene el entorno reproducible para cualquiera.

## Ejemplos
### Mal
```java
if (System.getenv("LOCAL") != null) {
    client = DynamoDbClient.builder().endpointOverride(URI.create("http://localhost:8000")).build();
}
```
### Bien
```yaml
# application-local.yaml
app:
  dynamodb:
    endpoint-override: http://dynamodb-local.demo.svc:8000
    region: eu-west-1
    access-key: example-local
    secret-key: changeme-local
```
```yaml
# README del perfil: límites declarados
not_reproduced:
  dynamodb: [global-tables, throttling, backups, eventual-consistency]
  s3: [cross-region-replication, full-object-lock]
```

## Checklist de revisión
- [ ] Cada emulador figura en `catalog/parity-matrix.yaml` con su `not_reproduced`.
- [ ] Endpoints y credenciales de ejemplo solo en el perfil local.
- [ ] Ninguna lógica de dominio depende de si hay emulador.
- [ ] Ningún texto sugiere verificación en AWS real.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de afirmaciones honestas | 1 | `factory/validators/honest_claims.py` |
| Hook al editar texto | 2 | `.claude/hooks/post-tool-use/maturity_label_check.py` |
| Contraste emulador vs. matriz | 3 | revisión humana (pendiente de automatizar) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `local-parity-matrix`, `local-profiles`, `cluster-tooling`, `honest-claims-policy`.
- Fuentes: `catalog/parity-matrix.yaml`; documentación de LocalStack (2026-11-07); imagen oficial DynamoDB Local (comprobar etiqueta).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
