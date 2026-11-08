---
name: backup-and-restore
description: "Usar al diseñar backups de recursos y volúmenes de Kubernetes con Velero (OSS), programación, retención y pruebas de restauración."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Backup y restore con Velero

## Cuándo aplicar y cuándo no
- Aplica al respaldo de objetos de Kubernetes (recursos, PVC) con Velero y su restauración.
- No aplica a backups nativos de bases de datos (CloudNativePG/barman, ver `operators`) ni a backups de nube (ver `backup-vault-immutability-and-restore-tests`).

## Reglas
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

## Por qué
Los volúmenes persistentes y los CRs de operators no están en Git. Un backup nunca restaurado es una hipótesis; el primer restore no debería ocurrir durante un incidente.

## Ejemplos
### Mal
```text
velero backup create manual-backup   # una vez, sin retencion ni prueba de restore
```
### Bien
```yaml
# Velero (apiVersion velero.io/v1, verificado 2026-11-08)
apiVersion: velero.io/v1
kind: Schedule
metadata: { name: daily-apps, namespace: velero }
spec:
  schedule: "0 2 * * *"
  template:
    ttl: 720h0m0s
    includedNamespaces: ["shop-*"]
    snapshotVolumes: true
```
```text
# Prueba trimestral
velero restore create --from-backup daily-apps-<timestamp> --namespace-mappings shop-orders-prod:restore-test
# verificar smoke tests, anotar RTO medido en docs/runbooks/restore-tests.md
```

## Checklist de revisión
- [ ] Schedule con ttl y destino externo cifrado.
- [ ] Restore probado en el último trimestre, con RTO anotado.
- [ ] Bases de datos con backup nativo/PITR.
- [ ] Sin credenciales en manifiestos.
- [ ] Alerta de backup fallido.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Revisión de Schedules y destino | 3 | agente revisor de manifiestos |
| Evidencia de restore test | 4 | revisión humana de `docs/runbooks/` del proyecto |

Alerta automática de backup fallido: pendiente.

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `operators`, `multi-cluster-and-dr`, `backup-vault-immutability-and-restore-tests`, `failover-and-failback-runbooks`.
- Fuentes: documentación de Velero (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
