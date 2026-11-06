# Formatos de configuración de Claude Code usados por la fábrica

> Verificado el 2026-11-06 contra https://code.claude.com/docs/en/ (hooks, sub-agents, skills, mcp, permissions). Revisar en cada `skill-review`. Lo no confirmado lleva `TODO-VERIFY`.

- **Hooks** (`.claude/settings.json`): `hooks.<Evento>[] = { matcher, hooks: [{ type: "command", command }] }`. Eventos usados: `SessionStart`, `PreToolUse`, `PostToolUse`, `Stop`. Entrada por stdin en JSON (`tool_name`, `tool_input`, `cwd`, `hook_event_name`…). Bloqueo: **exit code 2** con el motivo en stderr (o JSON `hookSpecificOutput.permissionDecision`). Ruta del proyecto: `${CLAUDE_PROJECT_DIR}`.
- **Subagentes** (`.claude/agents/**/*.md`): frontmatter `name`, `description` obligatorios; opcionales `tools`, `model`, `skills`, `permissionMode`… Las subcarpetas generan nombres con ámbito (`business/x.md` → `business:x`). TODO-VERIFY: comportamiento exacto del ámbito antes de la Oleada 5.
- **Skills**: `.claude/skills/<nombre>/SKILL.md` con `name` y `description` obligatorios; opcionales `metadata`, `allowed-tools`, `paths`… **Decisión:** estructura plana (ver ADR-0028); el bloque (01–31) y el nivel T1/T2/T3 van en `metadata`.
- **Comandos**: `.claude/commands/<nombre>.md` (admiten subcarpetas). TODO-VERIFY: los comandos están unificados con skills; confirmar antes de la Oleada 1.
- **`.mcp.json`**: `{ "mcpServers": { "<n>": { "type": "stdio|http|sse", ... } } }`.
- **Permisos**: `permissions.allow|ask|deny` con reglas `Tool(patrón)`.
