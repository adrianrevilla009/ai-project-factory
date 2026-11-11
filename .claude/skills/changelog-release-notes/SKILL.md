---
name: changelog-release-notes
description: "Usar al redactar el CHANGELOG y las notas de release de un proyecto: formato, audiencia, cambios incompatibles y avisos de migración."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "hook"
---

# Changelog y notas de release

## Cuándo aplicar y cuándo no
- Aplica a cada release de un servicio, librería o API consumida por terceros.
- No aplica a la automatización de versionado y tags (ver `release-versioning-changelog`) ni a mensajes de commit (ver `conventional-commits`).

## Reglas
- **MUST** mantener `CHANGELOG.md` con sección `Unreleased` arriba y versiones con fecha ISO `YYYY-MM-DD`.
- **MUST** agrupar por tipo: Added, Changed, Deprecated, Removed, Fixed, Security.
- **MUST** que los cambios incompatibles lleven la etiqueta `BREAKING`, el impacto y los pasos de migración.
- **MUST** que las notas de release se escriban para el consumidor (qué cambia para él), no para el desarrollador.
- **SHOULD** generar el borrador desde Conventional Commits y editarlo a mano antes de publicar.
- **SHOULD** enlazar PRs, ADRs y entradas del contrato OpenAPI afectadas.
- **MUST NOT** volcar el `git log` crudo como changelog.
- **MUST NOT** publicar notas que afirmen verificación en AWS real; la fábrica no despliega.

## Por qué
El changelog es el contrato humano de cambios: permite decidir si actualizar y qué migrar. Las categorías de "Keep a Changelog" son un estándar de facto y facilitan la lectura.

## Ejemplos
### Mal
```markdown
## 1.4.0
- fix stuff
- merge branch 'feature/x'
- wip
```
### Bien
```markdown
## [Unreleased]

## [1.4.0] - 2026-11-07
### Added
- `GET /orders/{id}/history` devuelve el historial de estados.
### Changed
- **BREAKING** `status` pasa de entero a cadena (`CREATED`, `PAID`).
  Migración: actualizar clientes a la versión 2 del contrato antes del 2027-01-31.
### Deprecated
- `GET /orders?state=` (usar `status`).
### Fixed
- Pedidos duplicados al reintentar con la misma `Idempotency-Key`.
```
Fuente de las categorías y del formato de fecha: https://keepachangelog.com/en/1.1.0/ (consultado 2026-11-07).

## Criterios de decisión y trampas
### Cómo decidir
- Un registro de cambios para quien consume el software, agrupado por tipo y con avisos de incompatibilidades; las notas de versión explican el efecto, no los commits.
- Se genera de los commits convencionales y se revisa.
### Trampas frecuentes
- Copiar la lista de commits.
- Omitir cambios incompatibles.
- Notas para el equipo y no para el usuario.
- Sin enlace a guías de migración.
- Registro distinto de lo publicado.
### Evidencia
- Cada versión publicada tiene notas con incompatibilidades y migración.

## Checklist de revisión
- [ ] Existe `Unreleased` y la versión nueva tiene fecha ISO.
- [ ] Cada entrada está en su categoría y redactada para el consumidor.
- [ ] Todo `BREAKING` incluye migración y plazo.
- [ ] La versión sigue SemVer coherente con los cambios.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Commit-msg con Conventional Commits (alimenta el borrador) | 2 | skill `conventional-commits` / hooks de la fábrica |
| CI que exige entrada en `CHANGELOG.md` en PRs con cambios de contrato | 1 | pendiente, en el proyecto generado |
| Revisión humana de las notas | 3 | revisión humana |

> Estado: el check de CI está pendiente.

## Relacionados, fuentes y mantenimiento
- Relacionados: `release-versioning-changelog`, `versioning-semver-snapshots`, `api-versioning-deprecation`, `conventional-commits`.
- Fuentes: https://keepachangelog.com/en/1.1.0/ (2026-11-07); SemVer en https://semver.org/.
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
