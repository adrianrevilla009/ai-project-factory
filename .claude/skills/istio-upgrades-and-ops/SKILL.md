---
name: istio-upgrades-and-ops
description: "Usar al instalar, actualizar o operar Istio: upgrades por revisión (canary), compatibilidad de versiones y comprobaciones previas."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Upgrades y operación de Istio

## Cuándo aplicar y cuándo no
- Aplica a la instalación inicial, actualizaciones de versión y operación diaria del plano de control.
- No aplica al upgrade de Kubernetes (ver `cluster-upgrades-and-drift`), aunque debe coordinarse con él.

## Reglas
- **MUST** fijar la versión de Istio en el repositorio (Helm values / IstioOperator-equivalente) y comprobar la matriz de compatibilidad con la versión de Kubernetes.
- **MUST** actualizar en una versión menor cada vez y revisar notas de versión y cambios incompatibles.
- **MUST** preferir upgrade canary por **revisión**: instalar `istiod` nuevo en paralelo, migrar namespaces cambiando la etiqueta `istio.io/rev` y reiniciar sus pods; retirar el antiguo al final.
- **MUST** ejecutar `istioctl x precheck` antes y `istioctl analyze` después.
- **MUST** tener `istiod` con varias réplicas, PDB y `requests` definidos.
- **SHOULD** actualizar primero un namespace de prueba y observar métricas antes de producción.
- **MUST** probar el rollback: la etiqueta de revisión anterior debe seguir disponible hasta validar.
- **MUST NOT** hacer upgrade in-place en producción sin plan de vuelta atrás.
- **MUST** declarar que los upgrades se ensayan en local (kind) y que no se verifican en AWS.

## Por qué
Los sidecars mantienen la versión con la que se inyectaron: durante un upgrade conviven versiones. Por revisión, el riesgo se reparte namespace a namespace y se puede revertir cambiando una etiqueta.

## Ejemplos
### Mal
```text
# Un solo paso, sin precheck ni plan de vuelta
istioctl upgrade -y   # sobre el clúster de producción
```
### Bien
```text
# 1) Comprobaciones previas
istioctl x precheck
# 2) Instalar la nueva revisión en paralelo (valores desde el repo)
helm upgrade --install istiod-1-xx istio/istiod -n istio-system --set revision=1-xx -f values.yaml
# 3) Migrar un namespace de prueba
kubectl label namespace orders-test istio.io/rev=1-xx istio-injection- --overwrite
kubectl rollout restart deployment -n orders-test
# 4) Validar
istioctl analyze -n orders-test
```
Versión `1-xx` es un marcador; sintaxis exacta de etiquetas y charts.

## Checklist de revisión
- [ ] Versión fijada y compatible con Kubernetes.
- [ ] Upgrade por revisión con namespace piloto.
- [ ] `precheck` y `analyze` ejecutados.
- [ ] Rollback documentado y probado.
- [ ] `istiod` con réplicas y PDB.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: versión de Istio no fijada o `latest` (pendiente) | 1 | `policies/opa-conftest/` (pendiente) |
| Revisión del plan de upgrade | 3 | agente `code-reviewer` |
| Aprobación de la ventana de cambio | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `cluster-upgrades-and-drift`, `sidecar-vs-ambient-decision`, `multi-cluster-mesh`, `upgrade-policy`.
- Fuentes: istio.io/latest/docs/setup/upgrade/canary/ y tabla de soporte de versiones.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
