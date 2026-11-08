---
name: rbac-and-service-accounts
description: "Usar al definir Roles, RoleBindings y ServiceAccounts de Kubernetes, o al enlazar pods con IAM de nube (IRSA/Pod Identity) con mínimo privilegio."
metadata:
  block: "13-kubernetes-and-istio"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# RBAC y ServiceAccounts

## Cuándo aplicar y cuándo no
- Aplica a RBAC dentro del clúster y a la identidad de los pods.
- No aplica a IAM de nube en sí (ver `cloud-iam-least-privilege`) ni a la autorización de la aplicación (ver `authz-rbac-abac-rebac`).

## Reglas
- **MUST** usar una ServiceAccount dedicada por workload; **MUST NOT** usar la `default`.
- **MUST** poner `automountServiceAccountToken: false` salvo que el pod llame a la API de Kubernetes.
- **MUST** preferir `Role`/`RoleBinding` por namespace; `ClusterRole` solo para recursos cluster-scoped o agregaciones.
- **MUST NOT** conceder `cluster-admin`, wildcards (`*`) en verbs/resources ni `secrets` get/list global a aplicaciones.
- **MUST** vincular a humanos mediante grupos del IdP (Keycloak/OIDC), no usuarios individuales.
- **MUST** revisar permisos peligrosos: `escalate`, `bind`, `impersonate`, `create pods/exec`, `create rolebindings`.
- **SHOULD** enlazar identidad de nube con IRSA o EKS Pod Identity (TODO-VERIFY cuál usa el proyecto) con un rol por ServiceAccount y condición de namespace/SA en la trust policy.
- **SHOULD** usar tokens proyectados con audiencia y expiración corta; **MUST NOT** crear tokens de larga duración en Secrets.
- Local: kind no reproduce IRSA/Pod Identity; se simula con credenciales example o un emulador.

## Por qué
Un pod comprometido hereda su ServiceAccount: si es `cluster-admin`, el clúster entero cae. Los wildcards crecen en silencio cuando se añaden CRDs.

## Ejemplos
### Mal
```yaml
kind: ClusterRoleBinding
metadata: { name: orders-admin }
roleRef: { kind: ClusterRole, name: cluster-admin, apiGroup: rbac.authorization.k8s.io }
subjects: [{ kind: ServiceAccount, name: default, namespace: shop-orders-prod }]
```
### Bien
```yaml
apiVersion: v1
kind: ServiceAccount
metadata: { name: orders, namespace: shop-orders-prod }
automountServiceAccountToken: false
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata: { name: orders-config-reader, namespace: shop-orders-prod }
rules:
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["orders-config"]
    verbs: ["get"]
```

## Checklist de revisión
- [ ] ServiceAccount propia, sin automount innecesario.
- [ ] Sin `cluster-admin` ni wildcards para apps.
- [ ] Bindings a grupos, no usuarios.
- [ ] Rol de nube con trust policy acotada a namespace/SA.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Kyverno/OPA: prohibir bindings a cluster-admin y wildcards | 1 | pendiente en `policies/kyverno/` |
| Revisión de RBAC | 3 | agente revisor de seguridad |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `container-and-k8s-security`, `cloud-iam-least-privilege`, `namespaces-quotas-multitenancy`, `authn-oidc-oauth2`.
- Fuentes: documentación de Kubernetes (RBAC good practices) y EKS (IRSA/Pod Identity) (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
