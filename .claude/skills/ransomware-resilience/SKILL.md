---
name: ransomware-resilience
description: "Usar al diseñar defensas y recuperación frente a ransomware: copias inmutables aisladas, segmentación, privilegios mínimos y pruebas de restauración."
metadata:
  block: "25-security-operations"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Resiliencia frente a ransomware

## Cuándo aplicar y cuándo no
- Aplica a decisiones de copias de seguridad, segmentación, privilegios y recuperación que determinan si un cifrado malicioso es un incidente o una catástrofe.
- No aplica a la gestión general de backups sin amenaza adversaria (ver `backup-and-restore`) ni a DR por fallo de infraestructura (ver `multi-cluster-and-dr`).

## Reglas
- **MUST** mantener copias inmutables (WORM) en una cuenta/dominio de administración distinto del de producción, de modo que unas credenciales de producción comprometidas no puedan borrarlas (ver `backup-vault-immutability-and-restore-tests`).
- **MUST** seguir el principio 3-2-1 como mínimo: 3 copias, 2 medios o dominios distintos, 1 aislada/inmutable.
- **MUST** probar la restauración completa de los sistemas críticos periódicamente y medir el RTO real frente al objetivo (ver `tier-model-and-rpo-rto`).
- **MUST** limitar privilegios y movimiento lateral: segmentación de red, cuentas administrativas separadas, MFA, sin credenciales de dominio en estaciones normales.
- **MUST** proteger el plano de control de las copias con MFA y aprobación de dos personas para borrar o acortar la retención.
- **MUST** mantener un plan de recuperación priorizado (qué se restaura primero) y reconstruir desde imágenes y código conocidos, no desde sistemas sospechosos.
- **SHOULD** vigilar señales tempranas: cifrado masivo de ficheros, borrado de snapshots, desactivación de agentes de seguridad.
- **SHOULD** conservar el plan de comunicación y los contactos legales fuera de los sistemas que pueden quedar cifrados.
- **MUST NOT** basar la estrategia en pagar el rescate; decisión y asesoramiento legal corresponden a la dirección y a los asesores, no a este skill.
- **MUST NOT** montar los repositorios de copia como volúmenes escribibles desde las cargas de producción.

## Por qué
Los atacantes de ransomware buscan y destruyen primero las copias. Si el borrado de backups requiere las mismas credenciales que ya tienen, la recuperación falla. La inmutabilidad, el aislamiento y la restauración ensayada son lo que permite no negociar.

## Ejemplos
### Mal
```text
Backups en el mismo bucket y cuenta que producción, borrables por el rol de la aplicación.
Nunca se restauró nada: se asume que funciona.
```
### Bien
```hcl
# Terraform ilustrativo (estático; la fábrica no despliega)
resource "aws_backup_vault" "isolated" {
  name = "isolated-vault"
}
resource "aws_backup_vault_lock_configuration" "isolated" {
  backup_vault_name   = aws_backup_vault.isolated.name
  min_retention_days  = 14
  max_retention_days  = 365
  changeable_for_days = 3   # compliance mode tras el periodo de gracia
}
```
```text
Runbook trimestral: restaurar "orders-db" en entorno aislado, validar checksums y
registrar RTO medido vs objetivo.
```

## Criterios de decisión y trampas
### Cómo decidir
- Copias inmutables y aisladas con restauración probada, segmentación para limitar la propagación y accesos privilegiados controlados; define el orden de recuperación.
- Prepara la decisión sobre rescates con legal y dirección, antes.
### Trampas frecuentes
- Copias accesibles con las mismas credenciales que los sistemas.
- Restauraciones no ensayadas.
- Red plana.
- Sin orden de recuperación de servicios.
- Decidir en caliente sin un marco previo.
### Evidencia
- Un ensayo de restauración desde copias aisladas con el tiempo real medido.

## Checklist de revisión
- [ ] Existe copia inmutable en dominio de administración separado.
- [ ] Borrar o acortar retención exige MFA y doble aprobación.
- [ ] Última restauración completa probada y RTO medido.
- [ ] Segmentación y cuentas admin separadas.
- [ ] Orden de recuperación documentado y accesible offline.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Conftest: vault de backup sin lock config | 1 | `policies/opa-conftest/backup-vault-lock.rego` |
| Prueba de restauración y decisiones de dirección | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `backup-vault-immutability-and-restore-tests`, `backup-and-restore`, `incident-response-playbooks-and-forensics`, `tier-model-and-rpo-rto`, `iam-governance-and-pam`.
- Fuentes: documentación de AWS Backup Vault Lock; guías de CISA sobre ransomware.
- Cloud: preparado para AWS, no verificado en real. En local no se reproduce Vault Lock ni aislamiento por cuentas; solo se ensaya el procedimiento de restauración.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
