---
name: conventional-commits
description: "Usar al redactar mensajes de commit o títulos de PR/squash, o al configurar la validación de commits y la generación automática de changelog."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Conventional Commits

## Cuándo aplicar y cuándo no
- Aplica a todo commit en la fábrica y en proyectos generados, y al título del PR (que se convierte en el commit del squash).
- No aplica a commits de merge automáticos de herramientas ni a historial importado previo a la adopción.

## Reglas
- **MUST** usar la forma `<tipo>[(ámbito)][!]: <descripción>` en imperativo, minúsculas, sin punto final, ≤ 72 caracteres.
- **MUST** usar tipos del conjunto: `feat`, `fix`, `docs`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. La especificación solo exige `feat` y `fix`; el resto es convención del equipo.
- **MUST** marcar cambios incompatibles con `!` antes de los dos puntos y/o un pie `BREAKING CHANGE: <descripción>` (en mayúsculas).
- **MUST** hacer commits pequeños y atómicos: una pieza lógica por commit, el build en verde en cada uno.
- **SHOULD** usar el cuerpo para el porqué (no el qué) y pies para `Refs: PAY-123` / `Closes #45`.
- **SHOULD** usar como ámbito el módulo o bounded context (`feat(billing): ...`).
- **MUST NOT** mezclar refactor y cambio funcional en un mismo commit.
- **MUST NOT** usar mensajes vacíos de significado (`wip`, `fix stuff`, `changes`).

## Por qué
La especificación 1.0.0 vincula tipos con SemVer: `fix` -> PATCH, `feat` -> MINOR, `BREAKING CHANGE` -> MAJOR. Eso permite calcular versión y generar changelog desde el historial sin trabajo manual, y hace el historial navegable. Fuente: https://www.conventionalcommits.org/en/v1.0.0/ (consultada 2026-11-07).

## Ejemplos
### Mal
```text
fixed stuff
Update OrderService.java
feat: Added the new refunds feature and also refactored the repository and bumped deps.
```
### Bien
```text
feat(refunds): add partial refund endpoint

Permite reembolsar un importe menor al total del pedido.
Refs: PAY-123
```
```text
refactor(orders)!: rename OrderStatus.CANCELLED to CANCELED

BREAKING CHANGE: el valor serializado del estado cambia en la API v1.
```
Validación local de ejemplo (expresión regular de cabecera):
```text
^(feat|fix|docs|refactor|perf|test|build|ci|chore|revert)(\([a-z0-9-]+\))?!?: .{1,72}$
```

## Checklist de revisión
- [ ] Cabecera cumple la expresión de arriba.
- [ ] El tipo refleja el efecto real (no `chore` para un cambio de comportamiento).
- [ ] Breaking changes marcados con `!` y/o pie `BREAKING CHANGE:`.
- [ ] Un commit = un cambio lógico; build verde.
- [ ] Referencia al ticket en pie.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook `commit-msg` / check de CI que valida la cabecera con la expresión del ejemplo | 1 | pendiente (lo incluye el proyecto generado; la fábrica solo da la guía, ADR-0038) |
| Revisión del título de PR y mensajes | 3 | agente `code-reviewer`, ver `pr-rules` |

> Estado: sin artefacto automático en la fábrica; hasta que exista, la regla es de revisión.

## Relacionados, fuentes y mantenimiento
- Relacionados: `git-workflow`, `pr-rules`, `changelog-release-notes`, `release-versioning-changelog`.
- Fuentes: https://www.conventionalcommits.org/en/v1.0.0/ (2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
