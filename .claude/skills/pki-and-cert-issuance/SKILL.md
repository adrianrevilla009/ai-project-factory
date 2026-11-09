---
name: pki-and-cert-issuance
description: "Usar al emitir certificados internos con el motor PKI de Vault (CA raíz offline, intermedia por región, roles y TTL cortos) y al integrarlos con cert-manager."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Vault: PKI y emisión de certificados

## Cuándo aplicar y cuándo no
- Aplica a certificados internos (mTLS entre servicios, brokers, Keycloak interno) emitidos por Vault.
- No aplica a certificados públicos de borde (ACM/Let's Encrypt) ni a la identidad de workloads de Istio, que tiene su propia CA (ver `crypto-tls-mtls-key-rotation` y el bloque de Istio); si se enlaza Istio a Vault, es una decisión explícita.
- Local: el motor PKI funciona en Vault dev. NO se reproduce ACM, ni CA privada de AWS, ni la caída de una región.

## Reglas
- **MUST** mantener la CA raíz fuera de línea (o en un Vault aislado) y firmar solo CA **intermedias**; el Vault operativo solo guarda la intermedia.
- **MUST** una intermedia por región (D10: clústeres independientes), firmada por la misma raíz, de modo que un cliente confíe en ambas regiones con una sola raíz.
- **MUST** definir roles PKI acotados: `allowed_domains`, `allow_subdomains`, `max_ttl` corto (horas/días), `key_type`/`key_bits` modernos (RSA 2048+ o EC P-256+), `enforce_hostnames=true`.
- **MUST NOT** crear roles con `allow_any_name=true` ni `allow_localhost` en producción.
- **SHOULD** emitir certificados de hoja de vida corta y renovarlos automáticamente (cert-manager con `ClusterIssuer` de tipo Vault, o agente/VSO) en lugar de revocar.
- **MUST** publicar CRL/OCSP o aceptar que la revocación es débil y compensarlo con TTL corto; configurar `issuing_certificates` y `crl_distribution_points` con la URL de la región.
- **SHOULD** activar `tidy` automático para purgar certificados expirados del almacenamiento Raft.
- **MUST NOT** exportar ni guardar claves privadas de la CA intermedia en el repo ni en logs.
- **MUST** documentar la rotación de la intermedia (cross-signing) antes de que caduque.

## Por qué
Una CA comprometida invalida toda la confianza. Raíz offline e intermedias regionales acotan el impacto y permiten que una región funcione sola. Los TTL cortos hacen que la revocación sea casi innecesaria, que es lo realista cuando CRL/OCSP no están disponibles durante un DR.

## Ejemplos
### Mal
```text
vault write pki/roles/any allow_any_name=true max_ttl=87600h
vault write pki/root/generate/internal common_name=example-root ttl=87600h   # raíz viva en el Vault operativo
```
### Bien
```text
vault secrets enable -path=pki_int_euw1 pki
vault secrets tune -max-lease-ttl=43800h pki_int_euw1
vault write pki_int_euw1/config/urls \
  issuing_certificates="https://vault.euw1.example.internal:8200/v1/pki_int_euw1/ca" \
  crl_distribution_points="https://vault.euw1.example.internal:8200/v1/pki_int_euw1/crl"
vault write pki_int_euw1/roles/orders-mtls \
  allowed_domains="orders.svc.cluster.local" allow_subdomains=true \
  enforce_hostnames=true key_type=ec key_bits=256 max_ttl=24h
```
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: vault-euw1
spec:
  vault:
    server: https://vault.euw1.example.internal:8200
    path: pki_int_euw1/sign/orders-mtls
    auth:
      kubernetes:
        role: cert-manager
        mountPath: /v1/auth/kubernetes
        serviceAccountRef: { name: cert-manager }
```
Campos de `ClusterIssuer` y de los roles PKI.

## Checklist de revisión
- [ ] Raíz offline; intermedia por región, firmada por la raíz común.
- [ ] Roles con dominios acotados y TTL corto; sin `allow_any_name`.
- [ ] Renovación automática (cert-manager/agente) probada.
- [ ] URLs de emisión/CRL por región; `tidy` configurado.
- [ ] Plan de rotación de la intermedia documentado.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Conftest: roles PKI con `allow_any_name` o `max_ttl` > umbral | 1 | pendiente: `policies/opa-conftest/` |
| Kyverno: exigir certificados con `duration` <= umbral | 1 | pendiente: `policies/kyverno/` |
| Revisión de la jerarquía de CA | 4 | revisión humana (security-reviewer) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `crypto-tls-mtls-key-rotation`, `rotation-and-leases`, `deployment-ha`, `zero-trust`.
- Fuentes (2026-11-07): https://developer.hashicorp.com/vault/docs/secrets/pki; https://cert-manager.io/docs/configuration/vault/.
- Estado: diseño; preparado para AWS, no verificado en real.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
