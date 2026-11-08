---
name: security-frontend
description: "Usar al escribir o revisar código React que renderiza HTML, carga scripts, define CSP/cabeceras o maneja datos sensibles en el navegador (XSS)."
metadata:
  block: "27-frontend-react"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Seguridad del frontend (XSS, CSP, navegador)

## Cuándo aplicar y cuándo no
- Aplica a render de contenido dinámico, enlaces, iframes, scripts de terceros, cabeceras del hosting estático y almacenamiento en navegador.
- No aplica a seguridad del API (ver `security-headers-cors-csrf`, `input-validation-output-encoding`). Dependencias npm: `supply-chain-npm`. Tokens y sesión: `auth-and-session`.

## Reglas
- **MUST NOT** usar `dangerouslySetInnerHTML`, `innerHTML` ni `eval`/`new Function` con datos no confiables; si es inevitable, sanear con una librería de sanitización mantenida (p. ej. DOMPurify,) y revisión explícita.
- **MUST NOT** construir URLs desde entrada de usuario sin validar el esquema (`javascript:`); permitir solo `https:`/`mailto:` en enlaces dinámicos.
- **MUST** publicar una CSP estricta basada en nonce o hash, `object-src 'none'`, `base-uri 'none'`, `frame-ancestors 'none'` (salvo necesidad), sin `unsafe-inline` ni `unsafe-eval` (MDN CSP, 2026-11-07).
- **MUST** desplegar la CSP primero en `Content-Security-Policy-Report-Only` con endpoint de informes y pasar a enforce tras revisar.
- **SHOULD** activar Trusted Types (`require-trusted-types-for 'script'`) en proyectos nuevos.
- **MUST NOT** guardar tokens ni PII en `localStorage`/`sessionStorage`; ver `auth-and-session`.
- **MUST** añadir `rel="noopener noreferrer"` a enlaces `target="_blank"` externos y `sandbox` a iframes de terceros.
- **SHOULD** usar Subresource Integrity en scripts/estilos de CDN externos; **SHOULD** minimizar scripts de terceros.
- **MUST NOT** incluir secretos en variables `VITE_*`/`NEXT_PUBLIC_*`: todo lo del bundle es público.

## Por qué
React escapa por defecto, pero las vías de escape (`dangerouslySetInnerHTML`, URLs, librerías de terceros) reintroducen XSS. La CSP es defensa en profundidad: limita el daño si algo se cuela. Las listas de dominios permitidos suelen ser evadibles; nonce/hash es la recomendación vigente.

## Ejemplos
### Mal
```tsx
<div dangerouslySetInnerHTML={{ __html: comment.body }} />
<a href={user.website}>web</a>
const API_KEY = import.meta.env.VITE_SECRET_KEY; // acabará en el bundle
```
### Bien
```tsx
import DOMPurify from "dompurify";
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(comment.body) }} />
const safe = /^https:\/\//.test(user.website) ? user.website : undefined;
<a href={safe} rel="noopener noreferrer" target="_blank">web</a>
```
### CSP (cabecera de CloudFront/servidor; ejemplo)
```text
Content-Security-Policy: script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'
```
Un hosting 100 % estático (S3 + CloudFront) no genera nonce por petición: usar hashes en build o una función de borde. Comprobar enfoque. No reproducible en local: cabeceras de CloudFront.

## Checklist de revisión
- [ ] Sin `dangerouslySetInnerHTML`/`innerHTML` sin sanear.
- [ ] CSP sin `unsafe-inline`/`unsafe-eval`, con informes.
- [ ] Enlaces externos con `rel` y esquemas validados.
- [ ] Ningún secreto en variables públicas del bundle.
- [ ] Scripts de terceros inventariados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Regla Semgrep contra `dangerouslySetInnerHTML` sin sanitizar | 1 | `policies/semgrep/frontend-dangerously-set-inner-html.yaml` |
| Regla Semgrep contra tokens en `localStorage` | 1 | `policies/semgrep/frontend-token-in-web-storage.yaml` |
| `eslint-plugin-react` `no-danger`, `jsx-no-target-blank` | 1 | `policies/frontend-boundaries/` (pendiente) |
| Revisión de CSP y terceros | 3 | agente `security-reviewer` / revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `auth-and-session`, `supply-chain-npm`, `security-headers-cors-csrf`, `input-validation-output-encoding`, `build-and-deploy`.
- Fuentes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP (2026-11-07); OWASP XSS Prevention Cheat Sheet (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
