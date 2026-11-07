---
name: vault-and-keycloak-dr
description: "Usar al diseñar backup, restauración y recuperación ante desastres de Vault OSS (un clúster por región) y de Keycloak, incluidos RPO/RTO y ensayos."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# DR de Vault y Keycloak

## Cuándo aplicar y cuándo no
- Aplica a los runbooks y la automatización de backup/restore de Vault OSS y Keycloak, y a su encaje en los tiers RPO/RTO del proyecto.
- No aplica a la alta disponibilidad dentro de un clúster (ver `deployment-ha`) ni a la estrategia general multi-región (ver bloque 19).

## Reglas
- **MUST** asumir que Vault OSS no incluye replicación de DR entre clústeres (es función Enterprise, fuera de alcance por D10/D16); la recuperación se basa en snapshots Raft y reconstrucción. TODO-VERIFY contra la documentación vigente de la versión fijada.
- **MUST** programar snapshots Raft (`vault operator raft snapshot save`) y copiarlos cifrados a almacenamiento fuera del clúster y de la región (en AWS, S3 con KMS: preparado para AWS, no verificado en real).
- **MUST** definir RPO = intervalo de snapshot y RTO medido, y ensayar la restauración en un clúster limpio al menos trimestralmente.
- **MUST** proteger por separado las claves de unseal/recovery y el material de auto-unseal: un snapshot sin ellos no sirve.
- **MUST** tener un runbook de pérdida total de región: Vault de la región superviviente no tiene los secretos del otro; los secretos fuente deben reconstruirse desde GitOps (config) y desde sistemas origen (credenciales dinámicas se regeneran).
- **MUST** respaldar la base de datos de Keycloak (realms, usuarios, clientes) con el mismo rigor que los datos de negocio, y mantener los realms exportados como código (`kc.sh export` o configuración declarativa) sin secretos reales.
- **MUST NOT** restaurar un snapshot en un clúster productivo sin segundo aprobador.
- **SHOULD** tratar el arranque en frío (Vault y Keycloak caídos) como dependencia circular a documentar: qué servicios arrancan sin ellos.
- **SHOULD** versionar la matriz "qué NO se reproduce en local": el auto-unseal con KMS y el backup a S3 no se reproducen en local.

## Por qué
Sin replicación DR en OSS, cada región es una isla: un buen snapshot y un runbook ensayado son el único plan. Keycloak sin su BD pierde identidades y sesiones; Vault sin sus claves de unseal es un blob inservible.

## Ejemplos
### Mal
```text
# Backup solo en el volumen del propio nodo, sin ensayo de restauración
cp -r /vault/data /vault/data.bak
```
### Bien
```text
vault operator raft snapshot save /backup/raft-example.snap
# cifrar, subir a almacenamiento externo, registrar checksum y fecha
vault operator raft snapshot restore /backup/raft-example.snap   # solo en el ensayo o con doble aprobación
```
```yaml
# CronJob (resumen): schedule "0 */6 * * *" -> RPO objetivo 6 h; alerta si el último snapshot > 7 h
```

## Checklist de revisión
- [ ] Snapshots programados, cifrados y fuera de la región; RPO declarado.
- [ ] Ensayo de restauración con RTO medido y fecha del último.
- [ ] Unseal/recovery keys custodiadas fuera del backup.
- [ ] BD de Keycloak en el plan de backup; realms como código.
- [ ] Runbook de pérdida de región y arranque en frío.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de runbooks y CronJob de backup | 3 | agente `code-reviewer` |
| Comprobación de existencia de CronJob de snapshot (Kyverno/Conftest) | 1 | pendiente (`policies/kyverno/`) |
| Evidencia del ensayo de restauración | 4 | revisión humana en el gate de resiliencia |

## Relacionados, fuentes y mantenimiento
- Relacionados: `deployment-ha`, `audit-and-break-glass`, `tier-model-and-rpo-rto`, `failover-and-failback-runbooks`, `envelope-encryption-and-kms`.
- Fuentes: ADR-0010 y ADR-0031; documentación de Vault (operator raft snapshot) y de Keycloak (export/import), TODO-VERIFY URLs y versiones. Diseño preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
