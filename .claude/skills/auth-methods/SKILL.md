---
name: auth-methods
description: "Usar al decidir cómo se autentican personas, pods y pipelines contra Vault (Kubernetes auth, JWT/OIDC con Keycloak, AppRole) y qué TTL y bindings aplicar."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Vault: métodos de autenticación

## Cuándo aplicar y cuándo no
- Aplica al configurar `vault auth enable`, roles de login y la identidad que presentan cargas de trabajo, CI y operadores.
- No aplica a la autorización posterior (ver `policies`) ni a la autenticación de usuarios finales de la app (Keycloak, `authn-oidc-oauth2`).
- Local: se puede usar Kubernetes auth contra kind/k3d; NO se reproduce IRSA ni el método `aws` con identidades IAM reales.

## Reglas
- **MUST** autenticar pods con el método `kubernetes` (ServiceAccount JWT), un rol por servicio y namespace, con `bound_service_account_names` y `bound_service_account_namespaces` explícitos (nunca `*`).
- **MUST** autenticar humanos con OIDC contra Keycloak (D12) y mapear grupos a políticas; **MUST NOT** crear usuarios `userpass` compartidos.
- **MUST** autenticar CI con JWT/OIDC (token de GitHub Actions) acotando `bound_claims` a repositorio y rama/entorno; **MUST NOT** guardar tokens Vault estáticos como secreto de CI.
- **SHOULD** limitar AppRole a casos sin identidad de plataforma; el `secret_id` debe ser de un solo uso y con TTL corto, y el `role_id` no es secreto pero tampoco se publica.
- **MUST** asignar `token_ttl` corto (p. ej. 15 min–1 h), `token_max_ttl` acotado y `token_policies` mínimas por rol; **MUST NOT** usar tokens sin expiración ni el root token salvo bootstrap.
- **MUST** usar `token_bound_cidrs` donde la red lo permita y `token_num_uses` para tokens de tarea única.
- **SHOULD** deshabilitar métodos sin uso y auditar `sys/auth`.
- **MUST** tener un clúster Vault por región: cada uno registra sus propios métodos y roles; la configuración se aplica desde el mismo código Terraform, no por replicación.

## Por qué
Un rol demasiado amplio convierte cualquier pod del namespace en cliente privilegiado. Los tokens de larga vida filtrados no caducan. Atar identidad a ServiceAccount/claims hace que el compromiso quede acotado y auditable.

## Ejemplos
### Mal
```text
vault write auth/kubernetes/role/app \
  bound_service_account_names="*" \
  bound_service_account_namespaces="*" \
  policies="admin" ttl=0
```
### Bien
```hcl
resource "vault_kubernetes_auth_backend_role" "orders" {
  backend                          = "kubernetes"
  role_name                        = "orders"
  bound_service_account_names      = ["orders"]
  bound_service_account_namespaces = ["orders-prod"]
  token_policies                   = ["orders-read"]
  token_ttl                        = 900
  token_max_ttl                    = 3600
}

resource "vault_jwt_auth_backend_role" "ci_deploy" {
  backend        = "jwt-github"
  role_name      = "ci-deploy"
  role_type      = "jwt"
  user_claim     = "repository"
  bound_audiences = ["https://vault.example.internal"]
  bound_claims = {
    repository = "acme-example/orders"
    ref        = "refs/heads/main"
  }
  token_policies = ["ci-deploy"]
  token_ttl      = 600
}
```
Nombres de recursos del provider `hashicorp/vault`: TODO-VERIFY contra la versión fijada.

## Checklist de revisión
- [ ] Ningún rol con `*` en ServiceAccount o namespace.
- [ ] TTL y max TTL cortos; sin tokens eternos.
- [ ] CI y humanos entran por OIDC/JWT con claims acotados.
- [ ] No hay root token ni `userpass` compartido en uso.
- [ ] Config de auth versionada en Terraform y aplicada a cada clúster regional.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Conftest: roles con `*` o TTL 0 en HCL/Terraform de Vault | 1 | pendiente: `policies/opa-conftest/` |
| Hook contra literales de tokens | 2 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Revisión de roles y claims | 3 | revisión humana (security-reviewer) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `policies`, `injection-patterns`, `authn-oidc-oauth2`, `cloud-iam-least-privilege`, `secrets-management`.
- Fuentes: https://developer.hashicorp.com/vault/docs/auth (consultada 2026-11-07, no verificados todos los parámetros: TODO-VERIFY `bound_claims`/`token_*` en la versión fijada).
- Estado: diseño; preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
