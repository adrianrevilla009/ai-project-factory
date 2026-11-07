---
name: image-signing-and-provenance
description: "Usar al firmar imágenes con cosign (keyless OIDC) y emitir atestaciones de procedencia SLSA y SBOM en el pipeline de release."
metadata:
  block: "15-artifacts-and-registry"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Firma de imágenes y procedencia (cosign, SLSA)

## Cuándo aplicar y cuándo no
- Aplica al job de release que publica imágenes OCI y a la verificación previa a promoción.
- No aplica a la verificación en el clúster (ver `admission-verification`) ni a la generación del SBOM (ver `sbom`).

## Reglas
- **MUST** firmar cada imagen por digest, nunca por tag, con cosign; preferir firma keyless con la identidad OIDC del runner de CI (sin claves persistentes) o claves en KMS.
- **MUST NOT** guardar claves de firma privadas en el repositorio ni en variables de CI de larga vida.
- **MUST** emitir atestaciones: procedencia SLSA y SBOM CycloneDX asociadas al digest (`cosign attest`).
- **MUST** verificar en el paso de promoción con `--certificate-identity` (o `-regexp`) y `--certificate-oidc-issuer` explícitos; **MUST NOT** verificar con comodines que acepten cualquier identidad.
- **MUST** declarar el nivel SLSA realmente alcanzado, con evidencia; **MUST NOT** afirmar un nivel sin evidencia (builds en runners efímeros, sin acceso manual).
- **SHOULD** usar Rekor público para keyless; si la política de privacidad lo impide, evaluar Sigstore privado (TODO-VERIFY coste operativo) o claves KMS.
- **MUST** copiar firmas y atestaciones al promover a ECR si se verifica en admisión desde ECR (comprobar que el adaptador las preserva, TODO-VERIFY).
- **SHOULD** limitar `id-token: write` al job de firma.

## Por qué
Un digest demuestra qué bytes son; una firma demuestra quién los produjo; la procedencia demuestra cómo. Con keyless la identidad es el workflow concreto, y no hay clave que robar. Sin verificar identidad exacta, cualquiera con una cuenta del mismo emisor OIDC pasaría la comprobación.

## Ejemplos
### Mal
```text
cosign sign --key cosign.key registry.example.com/shop/orders:latest
cosign verify --key cosign.pub registry.example.com/shop/orders:latest
```
(clave en el repo, tag mutable)
### Bien
```yaml
jobs:
  sign:
    permissions:
      id-token: write   # OIDC para keyless
      packages: read
    steps:
      - run: cosign sign --yes registry.example.com/shop/orders@${{ needs.build.outputs.digest }}
```
```text
cosign verify registry.example.com/shop/orders@sha256:<digest> \
  --certificate-identity "https://github.com/example-org/shop/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```
`--certificate-identity` y `--certificate-oidc-issuer` confirmados en https://docs.sigstore.dev/cosign/verifying/verify/ (2026-11-07). Formato exacto de la identidad del workflow y `--yes`: TODO-VERIFY.

## Checklist de revisión
- [ ] Firma por digest, keyless o KMS.
- [ ] Sin claves privadas en el repo.
- [ ] Verificación con identidad e issuer explícitos.
- [ ] Atestaciones de procedencia y SBOM adjuntas.
- [ ] Nivel SLSA declarado con evidencia.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Kyverno `verifyImages` keyless | 1 | `policies/kyverno/verify-image-signatures.yaml` |
| Escaneo de secretos (claves privadas) | 2 | hook de secretos (ver `secret-scanning-and-leak-response`) |
| Revisión del nivel SLSA declarado | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `supply-chain`, `sbom`, `admission-verification`, `promotion-between-environments`.
- Fuentes: Sigstore cosign https://docs.sigstore.dev/cosign/verifying/verify/ ; SLSA https://slsa.dev/spec/ (TODO-VERIFY versión de spec) — 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
