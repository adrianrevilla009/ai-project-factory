---
name: bootstrap-generated-project-claude-config
description: "Usar en /project-init para crear el .claude/, CLAUDE.md y hooks de un proyecto generado a partir de las guías de la fábrica (sin plantillas)."
metadata:
  block: "31-agentic-engineering"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "hook"
---

# Bootstrap del .claude/ de un proyecto generado

## Cuándo aplicar y cuándo no
- Aplica al iniciar un proyecto (`/project-init`) y al actualizarlo a una versión nueva de la fábrica (`/upgrade-project`).
- No aplica a la propia fábrica, que ya tiene su `.claude/`.

## Reglas
- **MUST** copiar los hooks de `.claude/hooks/` de la fábrica al proyecto (`pre-tool-use`, `post-tool-use`, `stop`, `session-start`, `audit`, `_lib.py`) y registrar el mismo bloque `hooks` en `<target>/.claude/settings.json`, sin rebajar ninguna regla.
- **MUST** crear `<target>/.claude/hooks/hooks-config.json` con `test_command` real del proyecto, `test_trigger_globs`, y los formateadores/linters verificados (`format_and_lint`).
- **MUST** crear `<target>/CLAUDE.md` corto (skill `claude-md-authoring`): rol del proyecto, comandos reales, reglas no negociables, enlace a perfil de dominio y a los skills activos.
- **MUST** copiar solo los skills T1 y los T2 activados por la entrevista (`active_modules`) a `<target>/.claude/skills/`, y registrar en `<target>/docs/active-skills.md` su origen y la versión de la fábrica.
- **MUST** copiar `catalog/forbidden-libraries.yaml` y los validadores `factory/validators/honest_claims.py` + `common.py` al proyecto (`<target>/catalog/`, `<target>/factory/validators/`).
- **MUST** pedir a un humano que cree `<target>/.factory/state.json` (fase `intake`) y la carpeta `approvals/`; los agentes no pueden escribirlos (hook).
- **MUST NOT** incluir secretos, credenciales cloud ni permisos amplios (`Bash(*)`) en `settings.json`.
- **SHOULD** añadir `deny` para `.env*` y `approvals/**` en `permissions`.
- **SHOULD** limitar los MCP del proyecto a los imprescindibles, con permisos mínimos (`mcp-governance`).

## Por qué
Un proyecto generado debe ser tan seguro como la fábrica: sin los mismos hooks, un agente podría escribir secretos, saltarse un gate o hacer afirmaciones deshonestas sobre AWS. Copiar solo los skills activos reduce el contexto cargado.

## Ejemplos
### Mal
```json
{ "permissions": { "allow": ["Bash(*)"] }, "hooks": {} }
```
### Bien
```json
{
  "hooks": {
    "PreToolUse": [
      { "matcher": "Write|Edit|MultiEdit", "hooks": [
        { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pre-tool-use/block_secrets.py\"" },
        { "type": "command", "command": "python3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/pre-tool-use/enforce_gate_approval.py\"" }
      ] }
    ]
  },
  "permissions": { "deny": ["Read(./.env)", "Write(./approvals/**)"] }
}
```

## Checklist de revisión
- [ ] Los 3 hooks de seguridad y los de post/stop están registrados.
- [ ] `hooks-config.json` tiene `test_command` que funciona.
- [ ] `CLAUDE.md` < 80 líneas, con comandos verificados.
- [ ] Solo skills activos copiados y `active-skills.md` escrito.
- [ ] Sin permisos amplios ni secretos.
- [ ] `.factory/state.json` y `approvals/` creados por un humano.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hooks copiados bloquean secretos, comandos peligrosos y avance sin aprobación | 2 | `.claude/hooks/pre-tool-use/` |
| Revisión de `/audit-project` | 3 | agente `security-reviewer` |
| Revisión humana del bootstrap en el Gate 0 | 4 | `gates/gate-0-intake.md` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `claude-md-authoring`, `gate-protocol`, `mcp-governance`, `skill-authoring-guide`.
- Fuentes: `docs/architecture/claude-code-formats.md` (verificado 2026-11-06), hooks y permisos en https://code.claude.com/docs/en/ (comprobar al revisar).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
