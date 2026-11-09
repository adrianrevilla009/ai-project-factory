---
name: git-workflow
description: "Usar al crear ramas, integrar cambios o decidir cómo versionar trabajo en un proyecto generado: trunk-based development con ramas cortas y feature flags."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "hook"
---

# Git workflow (trunk-based)

## Cuándo aplicar y cuándo no
- Aplica a todo repositorio de proyecto generado y a esta fábrica: cualquier rama, merge o reescritura de historial.
- No aplica a repos de terceros vendorizados ni a forks de solo lectura.
- Productos con varias versiones soportadas en paralelo pueden añadir ramas `release/*` (ver regla de release).

## Reglas
- **MUST** tener una única rama de integración (`main`), siempre desplegable en el sentido de que su pipeline está en verde.
- **MUST** trabajar en ramas cortas (objetivo: menos de 2 días de vida, un cambio pequeño) que se integran a `main` mediante PR.
- **MUST** nombrar ramas `<tipo>/<id-ticket>-<slug>` (`feat/PAY-123-refund-endpoint`), con los mismos tipos que `conventional-commits`.
- **MUST** ocultar trabajo incompleto detrás de un feature flag, no detrás de una rama larga viva.
- **MUST** hacer rebase de la rama sobre `main` antes del PR; el merge se hace en modo squash (un commit convencional por PR).
- **MUST NOT** hacer force push a `main` ni a ramas compartidas; **MUST NOT** `git reset --hard` sin revisar qué se pierde.
- **MUST NOT** commitear secretos, binarios generados ni `target/` / `node_modules/`.
- **SHOULD** proteger `main`: PR obligatorio, checks requeridos, sin push directo, historial lineal.
- **SHOULD** etiquetar releases con tags SemVer anotados `vMAJOR.MINOR.PATCH` desde `main` (o `release/*` si se soportan varias versiones).
- **SHOULD** borrar la rama tras el merge.

## Por qué
Las ramas largas acumulan divergencia y convierten la integración en un evento de riesgo. Integrar a menudo, con flags para lo inacabado, reduce el coste de los conflictos y mantiene el CI como señal real. El squash da un historial legible que alimenta changelog y versionado automáticos. Referencia de práctica: trunkbaseddevelopment.com (consultada 2026-11-07).

## Ejemplos
### Mal
```text
git checkout -b feature/big-refactor     # vive 3 semanas
git push --force origin main             # reescribe historial compartido
```
### Bien
```text
git switch main && git pull --ff-only
git switch -c feat/PAY-123-refund-endpoint
# ... commits pequeños ...
git fetch origin && git rebase origin/main
git push -u origin feat/PAY-123-refund-endpoint
# PR -> checks verdes -> squash merge -> borrar rama
```
Trabajo inacabado detrás de flag (propiedad de Spring Boot):
```java
@ConditionalOnProperty(name = "features.refunds.enabled", havingValue = "true")
@RestController
class RefundController { /* ... */ }
```

## Checklist de revisión
- [ ] La rama tiene menos de ~2 días y un solo propósito.
- [ ] Nombre de rama con tipo, ticket y slug.
- [ ] Rebase sobre `main` sin conflictos pendientes.
- [ ] Lo incompleto está tras un flag desactivado por defecto.
- [ ] Ningún force push ni commit directo a `main`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook que bloquea `git push --force` y `git reset --hard` | 1 | `.claude/hooks/pre-tool-use/block_dangerous_commands.py` |
| Hook que bloquea secretos en ficheros escritos | 1 | `.claude/hooks/pre-tool-use/block_secrets.py` |
| Branch protection de `main` en el proyecto generado (configuración del repo remoto) | 2 | pendiente (lo configura el equipo del proyecto) |
| Revisión de tamaño y vida de la rama | 3 | agente `code-reviewer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `conventional-commits`, `pr-rules`, `release-versioning-changelog`, `change-and-release-management`.
- Fuentes: https://trunkbaseddevelopment.com/ y https://semver.org/ (consultadas 2026-11-07); ajustes de branch protection de GitHub.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
