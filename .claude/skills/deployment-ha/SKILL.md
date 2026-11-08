---
name: deployment-ha
description: "Usar al diseñar o revisar el despliegue de Vault OSS: Raft de 3 AZ, auto-unseal con KMS y un clúster independiente por región (sin replicación Enterprise)."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Vault: despliegue HA, Raft y auto-unseal

## Cuándo aplicar y cuándo no
- Aplica al diseñar el clúster de Vault de un proyecto, su Helm/Terraform y el runbook de arranque.
- No aplica al uso de Vault por las aplicaciones (ver `injection-patterns`) ni al DR cruzado (ver `vault-and-keycloak-dr`).
- Local: el modo `dev` de Vault (un nodo, sin unseal, en memoria) solo sirve para desarrollo. NO se reproduce en local: Raft multi-AZ, auto-unseal con KMS ni fallo de región.

## Reglas
- **MUST** desplegar Vault OSS con almacenamiento integrado Raft, 3 nodos (5 si el tier lo exige), uno por AZ (D10, ADR-0010). Un nodo perdido de 3 mantiene quórum; dos no.
- **MUST** usar un clúster Vault **independiente por región**. **MUST NOT** asumir replicación de rendimiento/DR: es función Enterprise y de pago (D16). Si se documenta, solo como variante opcional.
- **MUST** configurar auto-unseal con KMS de la propia región (`seal "awskms"` con `region` y `kms_key_id`); la identidad de Vault (IRSA/rol de instancia) solo necesita `kms:Encrypt`, `kms:Decrypt`, `kms:DescribeKey` sobre esa clave.
- **MUST NOT** poner `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` en el stanza del seal ni en el repo.
- **MUST** custodiar las recovery keys (Shamir 5/3) con personas distintas, fuera de Vault y fuera del repo; el root token inicial se revoca tras el bootstrap.
- **MUST** habilitar TLS en listener API (8200) y clúster (8201); `tls_disable = true` está prohibido fuera de `dev`.
- **MUST** programar snapshots Raft (`vault operator raft snapshot save`) a un bucket de la misma región con cifrado, y ensayar la restauración.
- **SHOULD** usar Raft Autopilot para limpieza de nodos muertos y actualizaciones controladas.
- **SHOULD** fijar `topologySpreadConstraints` por zona y `PodDisruptionBudget` `maxUnavailable: 1`.
- **SHOULD** registrar la licencia: Vault es BUSL, OpenBao es la alternativa abierta (ADR-0031); comprobar licencia de la versión fijada con revisión legal.

## Por qué
Raft necesita mayoría viva; con 3 AZ se tolera una caída de zona. Sin auto-unseal, cada reinicio de pod deja el clúster sellado hasta intervención humana. Los clústeres por región fallan de forma independiente, a costa de no compartir estado: lo que deba cruzar regiones se resuelve fuera de Vault (ver `transit-encryption`, `envelope-encryption-and-kms`).

## Ejemplos
### Mal
```hcl
listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true
}
seal "awskms" {
  region     = "eu-west-1"
  kms_key_id = "alias/vault-unseal"
  access_key = "AKIAEXAMPLEchangeme"   # credencial en fichero
  secret_key = "changeme-example"
}
storage "file" { path = "/vault/data" } # un nodo, sin HA
```
### Bien
```hcl
ui = false
disable_mlock = true   # en K8s sin IPC_LOCK; comprobar según la política del clúster

listener "tcp" {
  address         = "0.0.0.0:8200"
  cluster_address = "0.0.0.0:8201"
  tls_cert_file   = "/vault/tls/tls.crt"
  tls_key_file    = "/vault/tls/tls.key"
}

seal "awskms" {                 # credenciales por IRSA, no en el fichero
  region     = "eu-west-1"
  kms_key_id = "alias/vault-unseal-eu-west-1"
}

storage "raft" {
  path    = "/vault/data"
  node_id = "vault-0"
  retry_join { leader_api_addr = "https://vault-1.vault-internal:8200" }
  retry_join { leader_api_addr = "https://vault-2.vault-internal:8200" }
}
api_addr     = "https://vault-0.vault-internal:8200"
cluster_addr = "https://vault-0.vault-internal:8201"
```

## Checklist de revisión
- [ ] 3 o 5 nodos Raft repartidos en AZ distintas, con PDB.
- [ ] Un clúster por región; ninguna dependencia de replicación Enterprise.
- [ ] Seal `awskms` regional, sin claves en el fichero; permisos KMS mínimos.
- [ ] TLS en 8200 y 8201; root token revocado; recovery keys repartidas.
- [ ] Snapshots Raft programados y restauración ensayada.
- [ ] Etiqueta de madurez: preparado para AWS, no verificado en real.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Hook que bloquea literales de credenciales | 2 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Conftest sobre values/HCL de Vault (`tls_disable`, storage no raft, claves en seal) | 1 | pendiente: `policies/opa-conftest/` |
| Revisión del diseño de HA y runbook de unseal | 3/4 | revisión humana (agente `code-reviewer` + owner) |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `vault-and-keycloak-dr`, `transit-encryption`, `secrets-management`, `crypto-tls-mtls-key-rotation`; ADR-0010, ADR-0031.
- Fuentes (consultadas 2026-11-07): https://developer.hashicorp.com/vault/docs/concepts/integrated-storage ; https://developer.hashicorp.com/vault/docs/configuration/seal/awskms. Comprobar tamaño de clúster recomendado y versión de Vault a fijar.
- Estado: diseño; preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
