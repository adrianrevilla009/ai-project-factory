---
name: release-versioning-changelog
description: "Usar al definir versionado semántico, tags, changelog y notas de release automatizadas desde Conventional Commits."
metadata:
  block: "16-ci-cd"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "hook"
---

# Versionado, release y changelog

## Cuándo aplicar y cuándo no
- Aplica a todo servicio o librería con releases etiquetadas.
- No aplica a la promoción entre entornos (ver `environment-promotion`) ni al versionado de APIs HTTP (`api-versioning-deprecation`).

## Reglas
- **MUST** usar SemVer 2.0.0 para librerías y servicios: MAJOR rompe compatibilidad, MINOR añade, PATCH corrige.
- **MUST** derivar el siguiente número de Conventional Commits (`feat`, `fix`, `feat!`/`BREAKING CHANGE:`), no de decisión manual ad hoc.
- **MUST** crear la release desde `main`, con tag anotado `vX.Y.Z` sobre el commit que pasó los gates; el tag no se mueve ni se reescribe.
- **MUST** que el artefacto lleve la versión y el SHA (labels OCI `org.opencontainers.image.version` y `.revision`) y se identifique por digest.
- **MUST** generar el changelog automáticamente (agrupado por tipo) y publicarlo en las notas de release.
- **SHOULD** versionar Maven con `revision` (CI-friendly) y evitar commits de "bump version" manuales.
- **MUST NOT** reutilizar ni sobrescribir una versión publicada; un error se corrige con un PATCH nuevo.
- **MUST NOT** publicar `-SNAPSHOT` a entornos distintos de dev.

## Por qué
Versiones inmutables y derivadas de commits hacen trazable qué código corre en cada entorno y permiten rollback exacto. El changelog automático evita notas inventadas a mano.

## Ejemplos
### Mal
```text
git tag -f v1.2.0     # mueve un tag ya publicado
mvn versions:set -DnewVersion=1.2.0   # a mano, sin relación con los commits
```
### Bien
```text
feat(orders): add bulk cancel endpoint        -> MINOR
fix(orders): avoid duplicate outbox rows      -> PATCH
feat(api)!: remove v1 order status field      -> MAJOR
```
```yaml
release:
  needs: [build, gates]
  runs-on: ubuntu-latest
  permissions: { contents: write }
  steps:
    - uses: actions/checkout@<SHA-40-HEX> # vX TODO-VERIFY
      with: { fetch-depth: 0 }
    - run:./scripts/release.sh   # calcula versión (herramienta a elegir: TODO-VERIFY), tag anotado y notas
```

## Checklist de revisión
- [ ] Commits siguen Conventional Commits.
- [ ] Tag anotado inmutable desde main tras gates verdes.
- [ ] Imagen con labels de versión/revisión y digest registrado.
- [ ] Changelog generado, no escrito a mano.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validación de mensaje Conventional Commits (hook commit-msg) | 2 | pendiente (`.claude/hooks/`) |
| Regla Rego: prohibir `git tag -f` y `push --force` en workflows | 1 | pendiente |
| Protección de tags en el repositorio | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `pipeline-architecture`, `supply-chain`, `api-versioning-deprecation`, `change-and-release-management`.
- Fuentes: https://semver.org/ y https://www.conventionalcommits.org/ (consultar 2026-11-07, TODO-VERIFY versión de cada especificación); regla 9 de `CLAUDE.md`.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
