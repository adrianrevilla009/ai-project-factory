---
name: ephemeral-preview-environments
description: "Usar al crear entornos efímeros por PR (namespace en Kubernetes) para pruebas de integración, contrato y rendimiento, con limpieza y coste acotado."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Entornos de preview efímeros

## Cuándo aplicar y cuándo no
- Aplica a proyectos que necesitan validar un PR contra dependencias reales antes del merge.
- No aplica a staging/producción permanentes ni a pruebas que Testcontainers cubre sin cluster.
- Local: kind/k3d (ADR-0034). En AWS equivale a un namespace en EKS, preparado para AWS, no verificado en real; no se reproduce en local el aislamiento de red ni los límites de cuenta.

## Reglas
- **MUST** crear un namespace por PR (`preview-pr-<n>`) con `ResourceQuota`, `LimitRange` y `NetworkPolicy` deny-by-default.
- **MUST** desplegar la imagen del PR por digest y los mismos manifiestos/chart que producción con valores de preview.
- **MUST** destruir el entorno al cerrar el PR y con un TTL (p. ej. 24 h) como red de seguridad.
- **MUST** usar datos sintéticos y secretos efímeros propios del preview; nunca datos reales ni secretos de otros entornos.
- **MUST NOT** exponer previews a Internet sin autenticación.
- **MUST NOT** permitir previews desde forks sin aprobación (ejecutan código no confiable).
- **SHOULD** limitar previews concurrentes por repositorio y etiquetar recursos con `pr`, `owner` y `expires-at` para FinOps.
- **SHOULD** ejecutar en el preview: smoke, contratos y perf corto (`deployment-verification-and-smoke`, `performance-gate`).

## Por qué
Un preview por PR da feedback con integración real sin contaminar entornos compartidos. Sin TTL ni cuotas, los previews olvidados cuestan dinero y ensanchan la superficie de ataque.

## Ejemplos
### Mal
```yaml
- run: kubectl apply -f k8s/ -n staging   # el PR pisa el entorno compartido
```
### Bien
```yaml
on: { pull_request: { types: [opened, synchronize, reopened, closed] } }
jobs:
  preview:
    if: github.event.action != 'closed'
    runs-on: ubuntu-latest
    environment: preview
    steps:
      - run: kubectl create namespace "preview-pr-${{ github.event.number }}" --dry-run=client -o yaml | kubectl apply -f -
      - run: >
          helm upgrade --install orders ./chart -n "preview-pr-${{ github.event.number }}"
          --set image.digest="$IMAGE_DIGEST" --set quota.enabled=true
  teardown:
    if: github.event.action == 'closed'
    runs-on: ubuntu-latest
    steps:
      - run: kubectl delete namespace "preview-pr-${{ github.event.number }}" --ignore-not-found
```
(Los `uses:` de configuración de kubeconfig se fijarían por SHA, comprobar al fijar la versión.)

## Checklist de revisión
- [ ] Namespace por PR con quota y NetworkPolicy.
- [ ] Teardown al cerrar y TTL.
- [ ] Datos sintéticos y secretos propios.
- [ ] Sin previews de forks sin aprobación.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Kyverno: exigir ResourceQuota/NetworkPolicy en namespaces `preview-*` | 1 | pendiente (`policies/kyverno/`) |
| Regla Rego: workflow de preview con job de teardown | 1 | pendiente |
| Revisión de costes de previews | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `performance-gate`, `contract-gate`, `finops`, `container-and-k8s-security`.
- Fuentes: ADR-0034, ADR-0005; Kubernetes ResourceQuota (https://kubernetes.io/docs/concepts/policy/resource-quotas/) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
