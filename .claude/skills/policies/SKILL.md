---
name: policies
description: "Usar al escribir o revisar políticas ACL de Vault (paths, capabilities, templating por identidad) para dar mínimo privilegio a servicios, CI y operadores."
metadata:
  block: "14-secrets-and-config"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Vault: políticas ACL

## Cuándo aplicar y cuándo no
- Aplica a ficheros `.hcl` de políticas, su asignación a roles y su despliegue por Terraform.
- No aplica a Sentinel/EGP/namespaces, que son funciones Enterprise (D16): no se asumen.
- No aplica a cómo se autentica el cliente (ver `auth-methods`).

## Reglas
- **MUST** escribir una política por servicio/función, con `path` concretos y las `capabilities` mínimas (`read` para leer; evitar `create`/`update`/`delete`/`sudo`).
- **MUST NOT** usar `path "*"`, `path "secret/*"` con `["create","read","update","delete","list","sudo"]`, ni políticas con `sudo` fuera de administración.
- **MUST** estructurar paths por entorno y servicio (`kv/data/<env>/<service>/*`); en KV v2 la política va sobre `data/` y `metadata/`, no sobre el path lógico.
- **SHOULD** usar templating de identidad (`{{identity.entity.aliases.<accessor>.metadata.service_account_namespace}}`) para una sola política reutilizable.
- **MUST** separar políticas de lectura de secretos, de emisión (`database/creds/*`, `pki/issue/*`, `transit/encrypt/*`) y de administración.
- **MUST** gestionar las políticas como código (Terraform `vault_policy`), revisadas en PR, y aplicarlas idénticas en cada clúster regional.
- **MUST NOT** conceder a una aplicación acceso a `sys/*`, `auth/*` ni a `transit/keys/*` (gestión de claves).
- **SHOULD** probar con `vault token capabilities <token> <path>` y tests negativos (debe fallar lo no concedido).
- **SHOULD** reservar `root` y la política administrativa para break-glass (ver audit-and-break-glass, pendiente de escribir).

## Por qué
El modelo de Vault es denegar por defecto; el riesgo está en políticas amplias "para que funcione". Un servicio comprometido solo debe poder leer lo suyo. En KV v2 el error más frecuente es escribir el path sin `data/` y obtener una política que no hace nada o que se amplía de más para "arreglarlo".

## Ejemplos
### Mal
```hcl
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list", "sudo"]
}
path "sys/*" { capabilities = ["sudo"] }
```
### Bien
```hcl
# orders-read.hcl : lectura de su KV y emisión de credenciales DB propias
path "kv/data/prod/orders/*" {
  capabilities = ["read"]
}
path "kv/metadata/prod/orders/*" {
  capabilities = ["list"]
}
path "database/creds/orders-rw" {
  capabilities = ["read"]
}
path "transit/encrypt/orders-pii" {
  capabilities = ["update"]
}
path "transit/decrypt/orders-pii" {
  capabilities = ["update"]
}
```
```hcl
resource "vault_policy" "orders_read" {
  name   = "orders-read"
  policy = file("${path.module}/policies/orders-read.hcl")
}
```
En Transit, encrypt/decrypt se conceden con `update`; comprobar en la documentación de la versión fijada.

## Checklist de revisión
- [ ] Sin `*` global ni `sudo` en políticas de aplicación.
- [ ] KV v2 con `data/` y `metadata/` correctos.
- [ ] Emisión (DB, PKI, Transit) separada de administración.
- [ ] Políticas en Terraform, con prueba de capabilities positiva y negativa.
- [ ] Misma política en cada clúster regional.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde |
|---|---|---|
| Conftest que rechaza `sudo`, `path "*"` y wildcards amplios en `.hcl` de Vault | 1 | pendiente: `policies/opa-conftest/` |
| Revisión de PR de políticas | 3 | revisión humana (security-reviewer) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `auth-methods`, `dynamic-database-credentials`, `transit-encryption`, `cloud-iam-least-privilege`.
- Fuentes: https://developer.hashicorp.com/vault/docs/concepts/policies (consultada 2026-11-07; comprobar sintaxis de templating y capabilities de Transit).
- Estado: diseño; preparado para AWS, no verificado en real.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
