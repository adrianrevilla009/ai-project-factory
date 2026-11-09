---
name: backup-vault-immutability-and-restore-tests
description: "Usar al diseñar backups inmutables (AWS Backup Vault Lock, copia cross-region/cuenta) y pruebas periódicas de restauración; cubre corrupción y ransomware que la replicación no resuelve."
metadata:
  block: "19-resilience-dr-finops"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Backups inmutables y pruebas de restauración

Aviso de nombres: aquí "vault" es el *backup vault* de AWS Backup, no HashiCorp Vault.

## Cuándo aplicar y cuándo no
- Aplica a todos los tiers (tier 3 se basa solo en esto) para Aurora, DynamoDB, S3 y volúmenes.
- No sustituye la replicación (RPO bajo) ni la complementa en latencia: protege frente a borrado, corrupción y cuenta comprometida.
- Diseño: preparado para AWS, no verificado en real. Local **no reproduce** backups gestionados ni Object Lock completo (MinIO).

## Reglas
- **MUST** copiar los backups a otra región (eu-central-1) y, preferiblemente, a otra cuenta de aislamiento.
- **MUST** activar Vault Lock con `min_retention_days` acorde a la política y `max_retention_days` para evitar costes eternos.
- **MUST** empezar en modo gobernanza o con `changeable_for_days` >= 3 (periodo de enfriamiento) y revisar antes de que sea inmutable; en modo cumplimiento, pasado ese plazo ni el titular ni AWS pueden quitar el bloqueo.
- **MUST NOT** usar retención "siempre" en recovery points de un vault en cumplimiento.
- **MUST** pruebas de restauración programadas (automatizar la restauración periódica; restaurar es operación de plano de control) y medir el tiempo real frente al RTO.
- **MUST** verificar integridad tras restaurar (conteos, checksums, consulta de negocio), no solo "estado completed".
- **SHOULD** Object Lock + versionado en S3 y PITR en DynamoDB y Aurora.
- **SHOULD** denegar por SCP/IAM `ec2:ModifySnapshotAttribute` y `ec2:ModifySnapshotTier` a roles ajenos al backup (el Vault Lock no gobierna llamadas directas a EC2).
- **MUST NOT** asumir que cerrar una cuenta conserva los backups: se borran tras 90 días.

## Por qué
La replicación propaga el borrado y la corrupción. Un backup que nadie ha restaurado es una hipótesis. El compromiso de cuenta es el escenario en que el aislamiento y la inmutabilidad importan.

## Ejemplos
### Mal
```hcl
resource "aws_backup_vault" "main" { name = "main" }   # sin lock, sin copia
```
### Bien
```hcl
resource "aws_backup_vault" "main" { name = "main" }

resource "aws_backup_vault_lock_configuration" "main" {
  backup_vault_name   = aws_backup_vault.main.name
  min_retention_days  = 35
  max_retention_days  = 365
  changeable_for_days = 7    # cumplimiento tras 7 días; revisar antes
}
```
Nombres de argumentos de Terraform: los recursos y sus argumentos de primer nivel se contrastaron con la documentación del provider AWS el 2026-11-08. Prueba:
```text
Trimestral: restaurar último recovery point de Aurora en eu-central-1 a un clúster de prueba,
ejecutar consulta de negocio de control, anotar duración, destruir el clúster.
```

## Criterios de decisión y trampas
### Cómo decidir
- Copias inmutables en una cuenta aislada con bloqueo de retención y pruebas periódicas de restauración automatizadas.
- Protege contra borrado malicioso y contra errores propios.
### Trampas frecuentes
- Copias en la misma cuenta que los datos.
- Restauraciones nunca probadas.
- Bloqueo configurado que se puede desactivar con un permiso común.
- Sin cifrado ni control de acceso.
- Objetivos de recuperación sin medir.
### Evidencia
- Un informe de restauración reciente con el tiempo real medido.

## Checklist de revisión
- [ ] Copia cross-region (y cross-account) configurada.
- [ ] Vault Lock con min/max y periodo de enfriamiento deliberado.
- [ ] Restauración probada con tiempo medido e integridad verificada.
- [ ] SCP que protege snapshots frente a modificaciones directas.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: `aws_backup_vault` sin lock con `min_retention_days` | 1 | `policies/opa-conftest/backup-vault-lock.rego` (validación estática de un plan; no desplegado) |
| Informe de última restauración probada | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `data-replication-matrix`, `finops-of-resilience`, `tier-model-and-rpo-rto`.
- Fuentes: AWS Backup Vault Lock, https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html y DR whitepaper (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
