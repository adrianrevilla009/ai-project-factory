---
name: build-and-deploy
description: "Usar al configurar el build con pnpm/Vite y el despliegue estático de la SPA (S3 + CloudFront): caché, invalidación, fallback SPA y multi-región."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Build y despliegue del frontend (pnpm, S3 + CloudFront)

## Cuándo aplicar y cuándo no
- Aplica al pipeline de build, al empaquetado estático, a las cabeceras de caché y a la definición Terraform del hosting estático.
- No aplica a SSR/Next (ver `rendering-strategy-decision`). La fábrica nunca despliega (ADR-0004): todo lo de AWS aquí es preparado para AWS, no verificado en real.

## Reglas
- **MUST** fijar versión de Node y de pnpm (`packageManager` en `package.json`, `.nvmrc`) y instalar con `pnpm install --frozen-lockfile` en CI.
- **MUST** construir una vez y promocionar el mismo artefacto entre entornos (`environment-promotion`); la configuración de entorno se resuelve en runtime (p. ej. `/config.json` servido sin caché), no recompilando.
- **MUST** servir `assets/*` con hash en el nombre con `Cache-Control: public, max-age=31536000, immutable` y `index.html` con `no-cache` (revalida siempre).
- **MUST** subir primero los assets con hash y por último `index.html`; invalidar en CloudFront solo `/index.html` y `/config.json`, no `/*`.
- **MUST** mantener el bucket S3 privado con acceso solo desde CloudFront (Origin Access Control), HTTPS obligatorio y cabeceras de seguridad (`security-frontend`).
- **MUST** devolver `index.html` para rutas de cliente (respuestas de error personalizadas 403/404 -> `/index.html` con 200, o función de borde) sin ocultar 404 de assets reales.
- **SHOULD** multi-región con bucket réplica (replicación entre regiones) y origin group de CloudFront con failover; documentar RTO/RPO (`tier-model-and-rpo-rto`).
- **SHOULD** publicar source maps solo en el sistema de errores (`observability-frontend`), no en el bucket público.
- **MUST NOT** incluir secretos en variables `VITE_*`: todo lo prefijado se incrusta en el bundle público.

## Por qué
Un `index.html` cacheado apuntando a assets borrados rompe la app tras un despliegue; el hash inmutable permite caché larga sin invalidaciones masivas. Construir una vez evita que lo probado difiera de lo desplegado.

## Ejemplos
### Mal
```text
aws s3 sync dist/ s3://example-bucket --delete        # index.html y assets con la misma caché
aws cloudfront create-invalidation --distribution-id EXAMPLE --paths "/*"
```
### Bien
```text
pnpm install --frozen-lockfile && pnpm build
aws s3 sync dist/assets s3://example-bucket/assets --cache-control "public,max-age=31536000,immutable"
aws s3 cp dist/index.html s3://example-bucket/index.html --cache-control "no-cache"
aws cloudfront create-invalidation --distribution-id EXAMPLE --paths "/index.html" "/config.json"
```
(Comandos ilustrativos, no ejecutados por la fábrica; verificar flags con la documentación de AWS CLI, TODO-VERIFY.)
```hcl
resource "aws_cloudfront_origin_access_control" "spa" {
  name                              = "spa-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}
```
Local: no se reproduce CloudFront ni OAC; se usa `vite preview` o nginx para probar el build y el fallback SPA.

## Checklist de revisión
- [ ] Node/pnpm fijados; instalación con lockfile congelado.
- [ ] Un solo build promocionado; config de entorno en runtime.
- [ ] Caché: assets inmutables, `index.html` no-cache.
- [ ] Bucket privado + OAC; fallback SPA correcto.
- [ ] Invalidación mínima; plan multi-región y de rollback (`rollback-strategy`).

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Checkov/OPA sobre Terraform (bucket sin acceso público, HTTPS) | 2 | `policies/iac-checks/`, `policies/opa-conftest/` (reglas específicas pendientes) |
| Pipeline con `--frozen-lockfile` y build único | 2 | pipeline del proyecto generado (pendiente) |
| Verificación de cabeceras tras despliegue | 3 | `deployment-verification-and-smoke` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `frontend-performance`, `security-frontend`, `environment-promotion`, `rollback-strategy`, `waf-shield-and-cloudfront`, `multi-region-patterns`.
- Fuentes: documentación de pnpm, Vite y de Amazon CloudFront/S3 (OAC, origin groups, invalidaciones) — TODO-VERIFY URLs y costes de invalidación; no consultadas 2026-11-07.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
