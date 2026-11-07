---
name: alternatives
description: "Usar solo si el proyecto no puede usar GitHub Actions: equivalencias y cautelas de GitLab CI y Jenkins respecto a las reglas de CI/CD de la fábrica."
metadata:
  block: "16-ci-cd"
  tier: T3
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Alternativas a GitHub Actions (T3)

## Cuándo aplicar y cuándo no
- Aplica solo cuando una restricción documentada (ADR del proyecto) impide GitHub Actions. Por defecto se usa D20 (ADR-0020).
- No aplica como comparativa de marketing; es una tabla de equivalencias de las reglas.

## Reglas
- **MUST** mantener las reglas de `pipeline-architecture` y los gates, independientemente de la herramienta.
- **MUST** registrar la excepción a D20 en un ADR del proyecto con motivo y coste de mantener guías duplicadas.
- **MUST** conservar los tres principios de D20: pipelines reutilizables, credenciales cortas por OIDC y dependencias fijadas inmutablemente.
- **SHOULD** preferir GitLab CI con `include:` de plantillas versionadas por SHA/tag protegido y `id_tokens` para OIDC (TODO-VERIFY sintaxis).
- **SHOULD** si se usa Jenkins: Jenkinsfile declarativo, shared libraries versionadas, agentes efímeros (pods) y plugins mínimos fijados.
- **MUST NOT** guardar claves de nube de larga vida en el servidor de CI ni ejecutar builds en el controlador de Jenkins.
- **MUST NOT** exigir licencias de pago por defecto (D16).

## Por qué
El valor está en los principios (reutilización, identidad federada, inmutabilidad), no en el producto. Jenkins añade el coste de operar y parchear el controlador y sus plugins.

## Ejemplos
### Mal
```groovy
pipeline { agent any  // corre en el controlador
  environment { AWS_SECRET_ACCESS_KEY = credentials('example-aws-key') } }
```
### Bien
Equivalencias (sintaxis por verificar en documentación oficial, TODO-VERIFY):
```text
GitHub Actions              GitLab CI                   Jenkins
workflow_call reutilizable  include: + templates         shared library
OIDC id-token               id_tokens: (JWT por job)     plugin OIDC / credenciales federadas
environment + revisores     environment + protected      input step + roles
pin por SHA                 include por ref inmutable    versión fija de library y plugins
runner efímero              runner autoescalado/K8s      agente pod efímero
```

## Checklist de revisión
- [ ] ADR de excepción a D20 registrado.
- [ ] Mismos gates y orden que `pipeline-architecture`.
- [ ] Sin credenciales largas ni builds en el controlador.
- [ ] Plantillas/librerías/plugins fijados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión del ADR de excepción | 4 | revisión humana |
| Políticas Rego equivalentes para `.gitlab-ci.yml`/Jenkinsfile | 1 | pendiente |

## Relacionados, fuentes y mantenimiento
- Relacionados: `github-actions`, `pipeline-architecture`, `security-gates`.
- Fuentes: ADR-0020; https://docs.gitlab.com/ci/ y https://www.jenkins.io/doc/ — TODO-VERIFY (no consultadas en esta revisión).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T3
