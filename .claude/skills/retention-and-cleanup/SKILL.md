---
name: retention-and-cleanup
description: "Usar al definir políticas de retención y limpieza de imágenes y paquetes (Harbor, Nexus, ECR) sin romper rollback ni trazabilidad."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Retención y limpieza de artefactos

## Cuándo aplicar y cuándo no
- Aplica a políticas de retención en repositorios de construcción (Harbor/Nexus/Reposilite) y en ECR.
- No aplica a retención de logs/backups (ver bloque 19) ni al borrado de datos personales.

## Reglas
- **MUST** definir retención por entorno: dev corta (p. ej. últimas N=10 o 14 días), staging media, prod larga; los valores concretos son decisión del proyecto.
- **MUST** conservar siempre los digests actualmente desplegados y los N últimos releases de prod para permitir rollback (ver `rollback-strategy`).
- **MUST NOT** borrar un digest referenciado por un manifiesto GitOps o por una atestación de release vigente.
- **MUST** ejecutar primero en modo simulación (dry-run) y revisar el listado antes de activar el borrado.
- **MUST** limpiar también capas huérfanas: en Harbor el borrado de artefactos no libera espacio hasta ejecutar el garbage collection (comprobar en docs de la versión usada).
- **SHOULD** excluir de la limpieza por regla lo marcado como `release` o con tag semver estable.
- **SHOULD** usar políticas de ciclo de vida de ECR para el registro runtime y repository creation templates para que los repos replicados las hereden (las políticas de ciclo de vida no se replican).
- **MUST** registrar en el puerto (`artifact-repository-port`) la política aplicada, para que sea revisable.

## Por qué
Sin retención el registro crece sin límite (coste, escaneos lentos). Con retención agresiva, un rollback a la versión anterior falla porque la imagen ya no existe. La regla es: borrar lo reproducible y sin referencias, nunca lo desplegado ni lo auditable.

## Ejemplos
### Mal
```text
# borra todo lo que tenga más de 7 días, también prod
retention: { keep_days: 7, scope: all-projects }
```
### Bien
```json
{
  "rules": [
    {
      "rulePriority": 1,
      "description": "keep last 20 release images",
      "selection": {"tagStatus": "tagged", "tagPrefixList": ["release-"], "countType": "imageCountMoreThan", "countNumber": 20},
      "action": {"type": "expire"}
    },
    {
      "rulePriority": 2,
      "description": "expire untagged after 7 days",
      "selection": {"tagStatus": "untagged", "countType": "sinceImagePushed", "countUnit": "days", "countNumber": 7},
      "action": {"type": "expire"}
    }
  ]
}
```
Formato de política de ciclo de vida de ECR; comprobar campos contra https://docs.aws.amazon.com/AmazonECR/latest/userguide/LifecyclePolicies.html antes de usar.

## Checklist de revisión
- [ ] Retención distinta por entorno, escrita en el repo.
- [ ] Digests desplegados y últimos releases de prod protegidos.
- [ ] Dry-run revisado antes de activar.
- [ ] GC/limpieza de capas planificada y monitorizada.
- [ ] Las políticas de ECR se aplican también a repos replicados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de la política de retención en PR | 3 | agente `code-reviewer` |
| Checkov/Conftest sobre `aws_ecr_lifecycle_policy` | 1 | pendiente (`policies/iac-checks/`) |
| Aprobación de borrados masivos | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `artifact-repository-port`, `promotion-between-environments`, `rollback-strategy`.
- Fuentes: ECR replication (no replica lifecycle policies) https://docs.aws.amazon.com/AmazonECR/latest/userguide/replication.html (verificado 2026-11-07); Harbor https://goharbor.io/docs/ (comprobar retention/GC).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
