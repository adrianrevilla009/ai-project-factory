---
name: software-templates
description: "Usar al diseñar plantillas de scaffolding (Backstage Scaffolder) que crean servicios nuevos con estándares, CI y catálogo ya incluidos."
metadata:
  block: "20-internal-developer-platform"
  tier: T2
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Software templates (Scaffolder)

## Cuándo aplicar y cuándo no
- Aplica cuando un equipo de plataforma ofrece "crear servicio nuevo" con autoservicio y quiere que cada servicio nazca conforme al estándar.
- No aplica a esta fábrica como contenido: la fábrica solo contiene guías (ADR-0038); las plantillas viven en el repositorio de plataforma del proyecto generado.

## Reglas
- **MUST** que la plantilla sea `kind: Template` con `apiVersion: scaffolder.backstage.io/v1beta3`, con `parameters`, `steps` (cada uno con `id`, `name`, `action`, `input`) y `output`.
- **MUST** que lo generado incluya: `catalog-info.yaml` con owner, pipeline CI, Dockerfile multistage, `docs/` + `mkdocs.yml`, y configuración de seguridad (SBOM, escaneo).
- **MUST** pedir `owner` con el selector de propietarios del catálogo (`OwnerPicker`), no texto libre.
- **MUST** versionar la plantilla (tag Git) y registrar en el servicio generado qué versión de plantilla lo creó.
- **SHOULD** mantener la plantilla mínima: lo opcional va en parámetros con valores por defecto seguros.
- **SHOULD** probar la plantilla en CI generando un servicio de muestra y ejecutando su build.
- **MUST NOT** incluir secretos ni credenciales reales en el esqueleto; solo referencias.
- **MUST NOT** dejar plantillas sin dueño: una plantilla obsoleta propaga deuda a cada servicio nuevo.

## Por qué
La plantilla es el punto de mayor palanca: un fallo en ella se copia a todos los servicios nuevos, y una mejora llega a todos los que nazcan después. Probarla en CI evita que el "camino pavimentado" se rompa sin que nadie lo note.

## Ejemplos
### Mal
```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: service
spec:
  owner: someone
  type: service
  parameters:
    - properties:
        owner: { type: string }     # texto libre
  steps:
    - id: fetch
      name: Fetch
      action: fetch:plain
      input: { url: ./skeleton }    # sin catalog-info ni CI
```
### Bien
```yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: java-spring-service
  title: Servicio Java Spring Boot
spec:
  owner: group:default/platform-team
  type: service
  parameters:
    - title: Datos
      required: [name, owner]
      properties:
        name: { type: string, pattern: '^[a-z][a-z0-9-]{2,30}$' }
        owner:
          type: string
          ui:field: OwnerPicker
  steps:
    - id: fetch
      name: Generar esqueleto
      action: fetch:template
      input:
        url: ./skeleton
        values: { name: '${{ parameters.name }}', owner: '${{ parameters.owner }}' }
    - id: register
      name: Registrar en el catálogo
      action: catalog:register
      input:
        repoContentsUrl: '${{ steps.publish.output.repoContentsUrl }}'
        catalogInfoPath: /catalog-info.yaml
  output:
    links:
      - title: Repositorio
        url: '${{ steps.publish.output.remoteUrl }}'
```
Nota: el ejemplo omite el paso `publish` (`id: publish`) por brevedad; la acción concreta (`publish:github`, `publish:gitlab`...) depende del SCM. Comprobar ids de acción `catalog:register` y `publish:*` en la versión instalada.

## Checklist de revisión
- [ ] La plantilla genera catalog-info, CI, Dockerfile, docs y seguridad.
- [ ] `owner` usa `OwnerPicker`.
- [ ] Hay test de CI que genera y construye un servicio de muestra.
- [ ] Sin secretos reales en el esqueleto.
- [ ] Versión de plantilla trazable desde el servicio.

## Enforcement
| Mecanismo | Nivel (1 policy · 2 hook · 3 revisor · 4 humano) | Dónde está |
|---|---|---|
| Test CI de generación de la plantilla | 1 | pendiente (repo de plataforma del proyecto) |
| Hook de bloqueo de literales tipo secreto | 2 | `.claude/hooks/` |
| Revisión de cambios de plantilla | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `backstage`, `golden-paths-governance`, `docker-multistage`, `sbom`.
- Fuentes (verificado 2026-11-07): https://backstage.io/docs/features/software-templates/writing-templates (apiVersion `scaffolder.backstage.io/v1beta3`, steps con id/name/action/input, `fetch:template`, `publish:github`, `OwnerPicker`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T2
