---
name: api-productization-and-developer-portal
description: "Usar al convertir una API en producto para terceros: claves y planes, portal de desarrolladores, sandbox, documentación, SDKs, cuotas, versionado y soporte."
metadata:
  block: "26-enterprise-capabilities"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Productización de APIs y portal de desarrolladores

## Cuándo aplicar y cuándo no
- Aplica a APIs expuestas a socios o desarrolladores externos con onboarding, credenciales, planes y soporte.
- No aplica a APIs internas entre servicios propios ni al diseño del contrato en sí (ver `openapi-contract-first`).

## Reglas
- **MUST** tratar la API como producto: propietario, ciclo de vida (preview, GA, deprecated, sunset), changelog público y política de versionado y deprecación (`api-versioning-deprecation`).
- **MUST** generar la documentación del portal desde el OpenAPI versionado en el repo; sin docs escritas a mano que diverjan.
- **MUST** ofrecer un sandbox aislado con datos ficticios y credenciales de prueba separadas de producción; sin acceso a datos reales.
- **MUST** autenticar a terceros con OAuth2 client credentials (o claves API para casos simples); las claves se guardan solo como hash, se muestran una vez y se pueden rotar y revocar.
- **MUST** asociar cada credencial a una aplicación, un tenant y un plan con cuotas y límites de tasa (`rate-limiting-quotas`); responder 429 con `Retry-After`.
- **MUST** usar scopes mínimos por aplicación y registrar el consentimiento del propietario.
- **MUST** devolver errores homogéneos (`ProblemDetail`, `code` estable) y un identificador de petición (`X-Request-Id`) para soporte.
- **MUST** pasar el contract gate (diff de OpenAPI) en CI antes de publicar; un cambio incompatible exige versión nueva (`contract-gate`).
- **MUST** medir uso por aplicación/plan (volumen, errores, latencia) sin etiquetas de alta cardinalidad en métricas; el detalle va a logs.
- **SHOULD** publicar colección de ejemplos y guía de inicio rápido que se ejecuten en CI contra el sandbox.
- **SHOULD** generar SDKs desde OpenAPI solo si hay capacidad de mantenerlos; marcar su versión soportada.
- **SHOULD** soportar webhooks firmados con reintentos y panel de entregas (`webhooks`).
- **MUST NOT** exponer endpoints internos o de admin en el mismo gateway/spec público.
- **MUST NOT** cambiar o eliminar campos sin el periodo de deprecación anunciado (plazo por decisión de producto/contrato).

## Por qué
Un tercero no puede leer tu código ni llamarte por Slack: la confianza viene de contratos estables, docs ejecutables, errores claros y límites previsibles. Generar docs y gate desde el mismo OpenAPI evita la deriva; el sandbox protege datos reales.

## Ejemplos
### Mal
```yaml
# spec público con endpoint interno y sin seguridad declarada
paths:
  /internal/reindex: { post: { responses: { "200": { description: ok } } } }
```
### Bien
```yaml
openapi: 3.0.3
info: { title: Partner API, version: "1.2.0" }
security: [ { oauth2: [ orders.read ] } ]
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.com/oauth/token
          scopes: { orders.read: Read orders }
paths:
  /v1/orders:
    get:
      responses:
        "200": { description: Orders page }
        "429": { description: Rate limit exceeded, headers: { Retry-After: { schema: { type: integer } } } }
```
```bash
# gate de compatibilidad en CI (herramienta a elegir)
oasdiff breaking openapi-prev.yaml openapi.yaml --fail-on ERR
```

## Checklist de revisión
- [ ] Ciclo de vida, changelog y política de deprecación publicados.
- [ ] Docs generadas del OpenAPI; sandbox con datos ficticios.
- [ ] Claves hasheadas, rotables y revocables; scopes mínimos.
- [ ] Planes con cuotas y 429 con `Retry-After`.
- [ ] Errores homogéneos con `X-Request-Id`.
- [ ] Contract gate en CI; spec público sin endpoints internos.
- [ ] Métricas de uso por plan.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Contract gate (diff OpenAPI) | 1 | skill `contract-gate` y `gates/` de la fábrica (revisar ruta concreta) |
| Revisión de spec público y planes | 3 | agente `code-reviewer` |
| Plazos de deprecación y condiciones comerciales | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Skills relacionados: `openapi-contract-first`, `api-versioning-deprecation`, `rate-limiting-quotas`, `webhooks`, `contract-gate`, `bff-and-api-gateway`, `backstage`, `api-docs`.
- Fuentes: especificación OpenAPI (spec.openapis.org) y RFC 9457 (Problem Details), consultadas 2026-11-07 a nivel conceptual.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T2
