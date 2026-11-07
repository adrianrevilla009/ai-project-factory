---
name: backstage
description: "Usar al montar o mantener un portal de desarrollador con Backstage: catalog-info.yaml, propiedad de componentes, scorecards y TechDocs."
metadata:
  block: "20-internal-developer-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Backstage: catálogo, scorecards y TechDocs

## Cuándo aplicar y cuándo no
- Aplica cuando una organización con varios equipos y servicios necesita un catálogo único (quién es dueño de qué), documentación junto al código y métricas de madurez.
- No aplica a un único equipo con pocos servicios: un README y un CODEOWNERS bastan; Backstage tiene coste operativo real (Node.js, base de datos, plugins).

## Reglas
- **MUST** que cada componente desplegable tenga un `catalog-info.yaml` en la raíz de su repositorio, con `spec.type`, `spec.lifecycle` y `spec.owner` (los tres son obligatorios para `Component`).
- **MUST** que `spec.owner` apunte a un grupo/equipo del catálogo, nunca a una persona individual ni a un valor vacío.
- **MUST** declarar dependencias (`dependsOn`, `providesApis`, `consumesApis`) para que el grafo del catálogo refleje la realidad.
- **MUST** publicar documentación con TechDocs (docs-as-code: `mkdocs.yml` + `docs/` en el mismo repo) en vez de wikis externas.
- **SHOULD** definir scorecards como reglas objetivas y automáticas (owner presente, runbook enlazado, SLO declarado, cobertura de SBOM), nunca como puntuación subjetiva.
- **SHOULD** usar autenticación OIDC contra Keycloak (D-identidad) y no el proveedor de invitados fuera de desarrollo local.
- **MUST NOT** usar plugins de pago por defecto (D16); preferir el núcleo OSS de Backstage.
- **MUST NOT** editar entidades a mano en la UI: la fuente de verdad es Git.

## Por qué
Un catálogo sin dueños verificables se pudre en meses. Con `catalog-info.yaml` versionado, el alta/baja de un servicio es un PR revisable y el catálogo se mantiene solo. TechDocs evita que la documentación viva lejos del código que describe. Los scorecards convierten estándares en señales visibles sin imponer bloqueos.

## Ejemplos
### Mal
```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: orders
spec:
  type: service
  lifecycle: production
  owner: adrian        # persona, no equipo
```
### Bien
```yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: orders-service
  description: Gestión de pedidos
  annotations:
    backstage.io/techdocs-ref: dir:.
    example.com/runbook: https://example.com/runbooks/orders
spec:
  type: service
  lifecycle: production
  owner: group:default/team-orders
  system: checkout
  dependsOn:
    - resource:default/orders-db
  providesApis:
    - orders-api
```

## Checklist de revisión
- [ ] Existe `catalog-info.yaml` válido con type, lifecycle y owner (grupo).
- [ ] Dependencias y APIs declaradas.
- [ ] `mkdocs.yml` y `docs/index.md` presentes; TechDocs compila.
- [ ] Los scorecards se calculan de datos automáticos.
- [ ] El catálogo se ingiere desde Git (locations), sin altas manuales.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Regla Rego/Conftest que exige owner de grupo en `catalog-info.yaml` | 1 | pendiente (`policies/opa-conftest/`) |
| Revisión de PR de entidades del catálogo | 3 | agente `code-reviewer` |
| Decisión de adoptar Backstage y plugins | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `software-templates`, `golden-paths-governance`, `developer-experience-metrics`, `sbom`.
- Fuentes (verificado 2026-11-07): https://backstage.io/docs/features/software-catalog/descriptor-format (apiVersion `backstage.io/v1alpha1`, spec.type/lifecycle/owner). TODO-VERIFY: anotación `backstage.io/techdocs-ref: dir:.` en la página de TechDocs (https://backstage.io/docs/features/techdocs/).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
