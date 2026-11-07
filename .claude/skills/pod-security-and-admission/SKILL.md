---
name: pod-security-and-admission
description: "Usar al configurar Pod Security Admission, Kyverno o ValidatingAdmissionPolicy para imponer reglas a los pods en el clúster; modos audit, warn y enforce."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Pod Security y admisión

## Cuándo aplicar y cuándo no
- Aplica a la configuración de admisión del clúster y a la adopción gradual de políticas.
- No aplica al contenido del securityContext de cada pod (ver `container-and-k8s-security` y `workload-baseline`) ni a verificación de firmas (ver `admission-verification`).

## Reglas
- **MUST** etiquetar cada namespace de aplicación con Pod Security Standards: `enforce: restricted` (o `baseline` con justificación), más `audit` y `warn` en `restricted`.
- **MUST** documentar excepciones (namespaces de sistema, CNI, mesh con init containers) con motivo y dueño.
- **MUST** desplegar un motor de políticas propio (Kyverno, OSS) para reglas que PSA no cubre: requests, probes, registros permitidos, sin `latest`.
- **MUST** introducir políticas nuevas en `Audit`, revisar informes y pasar a `Enforce` por entorno (dev, luego staging, luego prod).
- **SHOULD** valorar `ValidatingAdmissionPolicy` nativa (CEL) para reglas simples sin webhook; TODO-VERIFY versión mínima de Kubernetes.
- **MUST** configurar `failurePolicy` y exclusiones de los webhooks pensando en disponibilidad: un webhook caído no debe bloquear el clúster entero ni dejarlo sin control (decisión explícita).
- **MUST NOT** aplicar políticas Enforce directamente en prod sin periodo de Audit.
- **MUST** versionar las políticas en el repo y probarlas con casos que pasan y que fallan.

## Por qué
La admisión es el último punto donde se puede rechazar un manifiesto inseguro. Activar Enforce de golpe rompe despliegues; Audit primero da visibilidad sin interrupción.

## Ejemplos
### Mal
```yaml
metadata:
  name: shop-orders-prod   # namespace sin etiquetas PSA
```
### Bien
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: shop-orders-prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```
Política Kyverno en Audit primero (`validationFailureAction: Audit`), ver `policies/kyverno/workload-baseline.yaml`. Revisar con `kubectl get policyreport -A` (TODO-VERIFY nombre del recurso en la versión instalada).

## Checklist de revisión
- [ ] Namespaces con etiquetas PSA (enforce, audit, warn).
- [ ] Excepciones documentadas.
- [ ] Políticas nuevas en Audit antes de Enforce.
- [ ] `failurePolicy` de webhooks decidida y documentada.
- [ ] Casos de prueba positivos y negativos.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Políticas Kyverno versionadas | 1 | `policies/kyverno/` |
| Tests de políticas (Kyverno CLI) | 1 | pendiente |
| Revisión del paso Audit a Enforce | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `container-and-k8s-security`, `workload-baseline`, `namespaces-quotas-multitenancy`, `admission-verification`.
- Fuentes: Kubernetes (Pod Security Admission, ValidatingAdmissionPolicy) y Kyverno docs — TODO-VERIFY versiones, 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
