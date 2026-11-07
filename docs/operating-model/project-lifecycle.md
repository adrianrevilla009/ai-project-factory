# Ciclo de vida de un proyecto generado

Esta fábrica no contiene plantillas (ADR-0038): los comandos guían a los agentes para **crear el proyecto en un directorio destino** (`<target>`), fuera de este repo, siguiendo los skills.

## Estado del proyecto destino
- `<target>/.factory/state.json`: `{"phase": "<fase>", "factory_version": "<VERSION>", "active_modules": [...], "tier": 1}`. Lo actualiza **una persona** o el orquestador tras un gate aprobado; los agentes no pueden editarlo (hook `enforce_gate_approval`).
- `<target>/approvals/gate-N.json`: registros de aprobación humana (`gates/approval-record.schema.json`).
- Fases: `intake → plan → implementation → pull-request → release → cloud-readiness → close`.

## Flujo y comandos
| Fase | Comandos | Gate al terminar |
|---|---|---|
| intake | `/project-init` → `/project-discover` → `/capability-select` | Gate 0 |
| plan | `/project-plan` → `/project-plan-review` → `/project-plan-test` | Gate 1 |
| implementation | `/project-implement` → `/implement-review` → `/implement-test` | Gate 2 |
| pull-request | `/pr-create` → `/pr-review` → `/pr-fix` → `/pr-merge-ready` | Gate 3 |
| release | `/release-prepare` → `/release-verify` | Gate 4 |
| cloud-readiness | `/cloud-readiness-check` → `/cost-estimate` → `/dr-tabletop` | Gate 5 |
| close | `/project-retro` → `/lessons-capture` | — |
| mantenimiento | `/add-service` `/add-capability` `/audit-project` `/upgrade-project` `/dependency-update` `/skill-review` | según caso |

## Reglas
1. Cada comando termina **parando** y presentando evidencia contra el checklist del gate (`gate-protocol`).
2. El `.claude/` del proyecto destino (CLAUDE.md, hooks, settings) lo crean los agentes con los skills `claude-md-authoring`, `bootstrap-generated-project-claude-config` y los hooks de `.claude/hooks/` de esta fábrica como referencia.
3. La infraestructura AWS se escribe y valida estáticamente; nunca se despliega.
