---
name: secrets-in-gitops
description: "Usar al manejar secretos en repos GitOps con Argo CD: qué nunca va a Git y cómo inyectarlos con External Secrets o Vault."
metadata:
  block: "17-gitops-progressive-delivery"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Secretos en GitOps

## Cuándo aplicar y cuándo no
- Aplica a cualquier credencial, token o clave que una aplicación desplegada por Argo CD necesite.
- No aplica a la gestión interna de Vault (ver `secrets-management`, ADR-0010).

## Reglas
- **MUST NOT** commitear `Secret` con `data`/`stringData` reales en el repo GitOps.
- **MUST** gestionar los secretos en el clúster destino con un operador: External Secrets Operator o Vault Secrets Operator contra Vault OSS (ADR-0010/0031); Sealed Secrets como alternativa sin backend. El repo solo contiene la referencia (`ExternalSecret`).
- **MUST NOT** inyectar secretos en la generación de manifiestos (plugins tipo argocd-vault-plugin): Argo CD guarda manifiestos generados en la caché Redis en claro.
- **SHOULD** que la actualización del secreto esté desacoplada del sync de la aplicación.
- **SHOULD** rotar con TTL corto/credenciales dinámicas (ver `dynamic-database-credentials`).
- **MUST** pasar un escáner de secretos (gitleaks o similar) en el pre-commit y en CI del repo GitOps.
- **MUST NOT** usar licencias de pago por defecto (D16): Vault OSS/OpenBao, no Vault Enterprise.

## Por qué
Git conserva el historial para siempre: un secreto commiteado está comprometido aunque se borre. Es la recomendación de la documentación de Argo CD: operadores en el clúster destino, no plugins de generación.

## Ejemplos
### Mal
```yaml
apiVersion: v1
kind: Secret
metadata: {name: db-credentials}
stringData:
  password: changeme-in-git     # secreto en Git (aunque sea de ejemplo)
```
### Bien
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: {name: db-credentials, namespace: shop-prod}
spec:
  refreshInterval: 1h
  secretStoreRef: {name: vault-backend, kind: ClusterSecretStore}
  target: {name: db-credentials}
  data:
    - secretKey: password
      remoteRef: {key: shop/prod/db, property: password}
```
La versión `external-secrets.io/v1beta1` vs `v1`: comprobar contra el operador instalado.

## Checklist de revisión
- [ ] Ningún `Secret` con datos en el repo.
- [ ] Solo `ExternalSecret`/`SealedSecret`/referencias.
- [ ] Sin plugins que inyecten secretos al renderizar.
- [ ] Escáner de secretos activo.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Conftest: Secret con datos en manifiestos | 1 | `policies/opa-conftest/gitops-no-plain-secrets.rego` (escrita, sin ejecutar localmente) |
| Escáner de secretos en CI | 1 | pendiente (pipeline del proyecto generado) |
| Hook de seguridad de literales | 2 | `.claude/hooks/` |

Local: kind/k3d no reproduce Vault gestionado ni KMS de AWS; se usa Vault OSS en modo dev solo para pruebas.

## Relacionados, fuentes y mantenimiento
- Relacionados: `secrets-management`, `dynamic-database-credentials`, `repo-strategy`, `argo-cd`.
- Fuentes (verificadas 2026-11-07): https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/ · ADR-0010, ADR-0011.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
