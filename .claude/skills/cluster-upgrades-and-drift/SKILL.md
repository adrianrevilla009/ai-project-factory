---
name: cluster-upgrades-and-drift
description: "Usar al planificar upgrades de versión de Kubernetes/EKS, nodos y addons, o al detectar y corregir drift entre el estado deseado en Git/IaC y el clúster."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Upgrades de clúster y drift

## Cuándo aplicar y cuándo no
- Aplica a upgrades de plano de control, nodos, addons y CRDs, y a la gestión de drift.
- No aplica a upgrades de Istio (ver `istio-upgrades-and-ops`) ni al despliegue de aplicaciones.

## Reglas
- **MUST** mantener el clúster dentro de una versión de Kubernetes con soporte; revisar el calendario oficial cada trimestre (TODO-VERIFY ventanas de soporte de EKS).
- **MUST** actualizar de una versión menor cada vez, en este orden: plano de control, addons, nodos; probar antes en dev y staging.
- **MUST** revisar APIs deprecadas/eliminadas antes de cada upgrade con una herramienta de detección (p. ej. pluto o kubent, OSS; TODO-VERIFY) en CI.
- **MUST** tener PDB y topology spread (ver `workload-baseline`) para que el drain de nodos no corte servicio.
- **SHOULD** actualizar nodos reemplazándolos (nuevos pools/AMI) en lugar de parchear in-place.
- **MUST** definir el estado deseado en Git/Terraform; el drift se detecta con `terraform plan` programado y con la comparación de GitOps (ver `drift-and-self-heal-policy`).
- **MUST NOT** hacer cambios manuales con `kubectl edit` en prod; si es una emergencia, registrar y llevar el cambio a Git en 24 h.
- **MUST** tener un plan de rollback documentado (el plano de control EKS no admite downgrade: el rollback es restaurar o recrear; ver `backup-and-restore`).
- **MUST** que la fábrica solo valide estáticamente: no ejecuta upgrades (ADR-0004).

## Por qué
Las versiones sin soporte dejan de recibir parches de seguridad. Los upgrades grandes y poco frecuentes son los que fallan; los pequeños y regulares se vuelven rutina. El drift convierte el repositorio en una mentira.

## Ejemplos
### Mal
```text
kubectl edit deployment orders -n shop-orders-prod   # cambio manual sin PR
Upgrade de 1.N a 1.N+3 de golpe, sin revisar APIs eliminadas.
```
### Bien
```text
# Runbook upgrade (extracto)
1. Detectar APIs deprecadas:  pluto detect-files -d manifests/   (TODO-VERIFY herramienta/version)
2. Upgrade dev -> soak 3 dias -> staging -> soak 3 dias -> prod
3. Orden: control plane, addons (cert-manager, CNI, CSI), pools de nodos (reemplazo en rolling)
4. Validar: smoke tests + SLOs durante 1 h antes de continuar
5. Registrar versiones en docs/runbooks/upgrades.md
```
```text
# CI programado
terraform plan -detailed-exitcode   # exit 2 = drift -> abrir issue
```

## Checklist de revisión
- [ ] Versión dentro de soporte y calendario revisado.
- [ ] Una versión menor por vez, entornos en orden.
- [ ] APIs deprecadas revisadas en CI.
- [ ] PDB/spread verificados antes del drain.
- [ ] Drift monitorizado; sin ediciones manuales.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Detección de APIs deprecadas en CI | 1 | pipeline del proyecto generado (pendiente) |
| `terraform plan` programado para drift | 1 | pipeline del proyecto generado (pendiente) |
| Aprobación del upgrade en prod | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `istio-upgrades-and-ops`, `cluster-addons-baseline`, `drift-and-self-heal-policy`, `change-and-release-management`.
- Fuentes: Kubernetes (version skew policy, deprecation guide) y EKS (versiones y upgrades) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
