---
name: api-docs
description: "Usar al documentar APIs REST o de eventos de un proyecto: OpenAPI/AsyncAPI como fuente única, ejemplos, errores y portal de consumo."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Documentación de APIs

## Cuándo aplicar y cuándo no
- Aplica a toda API expuesta fuera del módulo (REST, eventos Kafka) y a su publicación para consumidores.
- No aplica a clases internas (usar Javadoc solo donde aporte) ni al diseño del contrato (ver `openapi-contract-first`, `asyncapi-event-contracts`).

## Reglas
- **MUST** que la fuente de verdad sea el fichero de contrato versionado (`docs/api/openapi.yaml`, `docs/api/asyncapi.yaml`), no una wiki.
- **MUST** que cada operación tenga `summary`, `operationId` único, respuestas de error documentadas y al menos un ejemplo realista.
- **MUST** documentar autenticación (esquema OIDC/Keycloak), paginación, idempotencia y límites cuando existan.
- **MUST** que los cambios incompatibles pasen por `api-versioning-deprecation` y se anoten en el changelog.
- **SHOULD** generar el spec desde el código solo si se revisa el diff en el PR; con contract-first, generar el código desde el spec.
- **SHOULD** publicar el spec renderizado (Swagger UI/Redoc) junto al servicio en entornos no productivos.
- **MUST NOT** exponer la UI de documentación sin autenticación en entornos compartidos.
- **MUST NOT** incluir datos personales reales en ejemplos.

## Por qué
Los consumidores leen el contrato, no el código. Si el spec se desvía de la implementación, los consumidores se rompen en silencio; por eso el spec se valida en CI contra la implementación (contract tests).

## Ejemplos
### Mal
```yaml
paths:
  /orders:
    get:
      responses:
        "200": { description: OK }
```
### Bien
```yaml
paths:
  /orders/{id}:
    get:
      operationId: getOrder
      summary: Obtiene un pedido por id
      parameters:
        - { name: id, in: path, required: true, schema: { type: string, format: uuid } }
      responses:
        "200":
          description: Pedido encontrado
          content:
            application/json:
              example: { id: "0b6c1f1e-0000-4000-8000-000000000001", status: "CREATED" }
        "404":
          description: No existe
          content:
            application/problem+json:
              example: { type: "about:blank", title: "Not Found", status: 404 }
```
Si se usa springdoc-openapi, el spec se sirve por defecto en `/v3/api-docs` (fuente: https://springdoc.org/, consultado 2026-11-07). Comprobar versión del starter compatible con la versión de Spring Boot elegida.

## Checklist de revisión
- [ ] El spec está versionado y el PR muestra su diff.
- [ ] Toda operación tiene ejemplo y errores documentados.
- [ ] Seguridad, paginación e idempotencia descritas.
- [ ] Cambios incompatibles registrados en changelog y versión.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Lint del spec (p. ej. Spectral) y comparación de compatibilidad en CI | 1 | pendiente, en el proyecto generado |
| Gate de contrato | 2 | skill `contract-gate` |
| Revisión humana de ejemplos y descripciones | 3 | revisión humana |

> Estado: los artefactos de lint están pendientes.

## Relacionados, fuentes y mantenimiento
- Relacionados: `openapi-contract-first`, `asyncapi-event-contracts`, `api-versioning-deprecation`, `contract-testing`, `changelog-release-notes`.
- Fuentes: https://springdoc.org/ (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
