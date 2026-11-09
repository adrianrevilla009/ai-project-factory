---
name: deployment-verification-and-smoke
description: "Usar al definir cómo el pipeline verifica un despliegue: readiness, smoke tests, comprobación de versión y criterios para continuar o revertir."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "policy"
---

# Verificación de despliegue y smoke tests

## Cuándo aplicar y cuándo no
- Aplica tras cada despliegue a cualquier entorno (preview, dev, staging, prod).
- No aplica al análisis progresivo de canary con métricas (bloque 17, `argo-rollouts`); esto es la verificación mínima del pipeline.

## Reglas
- **MUST** esperar al rollout (`kubectl rollout status --timeout=...`) antes de declarar éxito; un `apply` sin espera no verifica nada.
- **MUST** ejecutar smoke tests tras el despliegue: endpoint de salud (readiness), una operación de lectura y una escritura idempotente de extremo a extremo con datos sintéticos.
- **MUST** comprobar que la versión desplegada es la esperada (digest/`/actuator/info`), para no probar la versión anterior por error.
- **MUST** que el smoke tenga timeout y reintentos acotados, y falle el job si no pasa; el fallo dispara `rollback-strategy`.
- **SHOULD** consultar las métricas RED del servicio durante una ventana corta tras el despliegue (tasa de error y latencia) con umbrales del SLO.
- **MUST NOT** usar `sleep` fijo como verificación; sondear con condición y timeout.
- **MUST NOT** ejecutar smoke destructivo ni con datos reales en producción.

## Por qué
Un despliegue "verde" en Kubernetes solo significa que los manifiestos se aplicaron. La verificación convierte "desplegado" en "funciona y es la versión correcta", y da la señal automática para revertir.

## Ejemplos
### Mal
```yaml
- run: kubectl apply -f k8s/ && sleep 30 && echo done
```
### Bien
```yaml
- run: kubectl -n "$NS" rollout status deploy/orders --timeout=180s
- name: version check
  run: |
    for i in $(seq 1 12); do
      v=$(curl -fsS "$BASE_URL/actuator/info" | jq -r .build.revision) && [ "$v" = "$GITHUB_SHA" ] && exit 0
      sleep 10
    done
    echo "version mismatch" >&2; exit 1
- name: smoke
  run: ./scripts/smoke.sh "$BASE_URL"   # health + lectura + escritura idempotente
```

## Criterios de decisión y trampas
### Cómo decidir
- Un `apply` correcto no significa que funcione: espera al rollout y comprueba.
- Smoke mínimo y estable: salud, una lectura y una escritura de bajo riesgo; el resto, en pruebas previas.
- Comprueba que la versión desplegada es la esperada para no probar la anterior.
### Trampas frecuentes
- Smoke que depende de datos de producción o los modifica.
- Fallos intermitentes del smoke que se acaban ignorando.
- Declarar éxito sin esperar a que los pods estén listos.
- Verificación que pasa por una caché y no por el servicio.
- Sin acción definida cuando falla.
### Evidencia
- El pipeline falla y revierte automáticamente si el smoke no pasa en un tiempo acotado.

## Checklist de revisión
- [ ] Se espera el rollout con timeout.
- [ ] Smoke cubre salud, lectura y escritura sintética.
- [ ] Se verifica la versión desplegada.
- [ ] El fallo activa el rollback.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Rego: job de despliegue debe incluir `rollout status` | 1 | pendiente |
| Semgrep sobre `sleep` en tests | 1 | `policies/semgrep/java-sleep-in-tests.yaml` (solo tests Java) |
| Revisión de la cobertura del smoke | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rollback-strategy`, `actuator-and-health`, `argo-rollouts`, `database-migration-step`.
- Fuentes: https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_status/.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
