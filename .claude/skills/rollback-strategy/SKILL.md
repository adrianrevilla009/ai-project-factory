---
name: rollback-strategy
description: "Usar al diseñar cómo revertir un despliegue desde el pipeline: rollback de aplicación, compatibilidad de esquema, feature flags y roll-forward."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Estrategia de rollback

## Cuándo aplicar y cuándo no
- Aplica a todo servicio desplegado por el pipeline.
- No aplica a la recuperación ante desastre regional (bloque 19, `failover-and-failback-runbooks`).

## Reglas
- **MUST** poder volver a la versión anterior redesplegando su digest inmutable, sin recompilar (`pipeline-architecture`).
- **MUST** conservar el digest y la configuración de la última versión estable por entorno (registro de despliegues).
- **MUST** que cada release sea compatible con la anterior a nivel de esquema y mensajes (expand/contract, `backward-compatibility-rules`); el rollback de app no revierte la BD.
- **MUST** automatizar el rollback ante fallo de `deployment-verification-and-smoke` y documentar el disparo manual (workflow `workflow_dispatch` con el digest como entrada).
- **SHOULD** desacoplar despliegue de activación con feature flags: apagar el flag es el rollback más rápido.
- **SHOULD** preferir roll-forward cuando el fallo es un bug pequeño y la migración ya es irreversible; decidirlo con criterio explícito.
- **MUST NOT** revertir migraciones destructivas ejecutando "down" improvisados; usar backup/restauración probados (`backup-vault-immutability-and-restore-tests`).
- **MUST** registrar el rollback (`record-deployment` en Pact, evento de despliegue para DORA).

## Por qué
La mayoría de rollbacks fallan por el esquema, no por la aplicación. Si la versión N-1 funciona con el esquema N, revertir es redesplegar un digest: rápido, probado y sin decisiones bajo presión.

## Ejemplos
### Mal
```text
git revert + rebuild + esperar 25 minutos de pipeline en plena incidencia
flyway undo en producción sin backup
```
### Bien
```yaml
on:
  workflow_dispatch:
    inputs:
      digest: { description: "sha256 de la versión estable", required: true }
      environment: { description: "dev|staging|prod", required: true }
jobs:
  rollback:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    steps:
      - run: >
          helm upgrade orders ./chart -n "$NS" --reuse-values
          --set image.digest="${{ inputs.digest }}" --atomic --timeout 5m
      - run: ./scripts/smoke.sh "$BASE_URL"
```
`--atomic` y flags de Helm. Si el entorno usa GitOps, el rollback es un revert en el repositorio de configuración (bloque 17).

## Criterios de decisión y trampas
### Cómo decidir
- Volver atrás redesplegando el digest anterior es lo normal; arreglar hacia delante solo si es más rápido y seguro.
- La compatibilidad de esquema y de mensajes entre versiones es lo que permite revertir; sin ella el rollback es una ilusión.
- Decide el disparador (métrica, tiempo, persona) antes del despliegue.
### Trampas frecuentes
- Un rollback que nunca se ha ensayado.
- Migraciones irreversibles sin plan de compensación.
- Perder la configuración de la versión anterior.
- Revertir el código y dejar mensajes ya publicados en un formato nuevo.
- Depender de que quien conoce el procedimiento esté disponible.
### Evidencia
- Un ensayo de rollback registrado en preproducción y el digest estable de cada entorno anotado.

## Checklist de revisión
- [ ] Digest estable anterior accesible y registrado.
- [ ] Esquema compatible N-1/N.
- [ ] Rollback automático y manual documentados y ensayados.
- [ ] Feature flags para funcionalidad de riesgo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Semgrep sobre migraciones incompatibles | 1 | `policies/semgrep/sql-unsafe-migrations.yaml` |
| Ensayo de rollback en staging | 4 | revisión humana (gate-4, `gates/gate-4-release.md`) |
| Revisión del plan de rollback en la PR | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `database-migration-step`, `deployment-verification-and-smoke`, `schema-migrations`, `change-and-release-management`, `environment-promotion`.
- Fuentes: documentación de Helm upgrade/rollback (https://helm.sh/docs/helm/helm_upgrade/).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
