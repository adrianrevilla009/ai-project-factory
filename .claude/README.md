# .claude

Configuración de Claude Code **de la fábrica**: lo que usan los agentes cuando trabajan sobre este repo. Los proyectos generados no heredan esta carpeta; sus agentes crean la suya con la skill `bootstrap-generated-project-claude-config`.

| Ruta | Contenido |
|---|---|
| `settings.json` | Registro de hooks y permisos. Deniega lectura/escritura de `.env*` y escritura en `approvals/**`. |
| `agents/` | 25 subagentes en 5 áreas: `business`, `delivery`, `engineering`, `quality`, `governance`. Los de governance son de solo lectura. |
| `commands/` | 26 comandos agrupados por fase: `00-intake` … `06-close`, más `maintenance`. |
| `skills/` | 490 skills, una carpeta por skill con su `SKILL.md`, más `_template/` con la plantilla. Índice navegable en [`docs/skills-index.md`](../docs/skills-index.md). |
| `hooks/` | Scripts Python deterministas. Detalle abajo. |

## Hooks
Cada hook lee el evento JSON por stdin; el código de salida 2 bloquea la acción (en `UserPromptSubmit` se bloquea con `{"decision":"block"}`, y `SessionEnd` no puede bloquear). Configuración en `hooks/hooks-config.json`, utilidades comunes en `hooks/_lib.py`. Tests en `tests/hooks/`.

| Evento | Hook | Qué hace |
|---|---|---|
| PreToolUse | `block_secrets` | Rechaza escrituras con credenciales (claves AWS, tokens de GitHub, claves privadas) y ficheros `.env`. |
| PreToolUse | `block_dangerous_commands` | Rechaza `rm -rf /`, `git push --force`, `terraform apply -auto-approve`, `curl … \| sh`, `kubectl delete ns`, etc. |
| PreToolUse | `enforce_gate_approval` | Impide editar código si faltan registros de aprobación válidos para la fase; impide que un agente escriba `approvals/` o `.factory/state.json`. |
| PreToolUse | `block_forbidden_paths` | Protege `.git/`, `node_modules/`, `.terraform/`, `*.tfstate`, `.claude/settings.json` y `.claude/hooks/`. |
| PostToolUse | `format_and_lint` | Ejecuta el formateador/linter configurado por patrón de fichero. |
| PostToolUse | `forbidden_deps` | Bloquea dependencias de `catalog/forbidden-libraries.yaml` (p. ej. Lombok). |
| PostToolUse | `architecture_guard` | Bloquea imports de framework dentro de `domain/`. |
| PostToolUse | `maturity_label_check` | Bloquea afirmaciones de que algo está verificado o listo en AWS real. |
| PostToolUse | `update_docs` | Anota qué código cambió para exigir documentación al parar. |
| PostToolUse | `prompt_injection_guard` | Avisa cuando un resultado externo contiene instrucciones sospechosas. |
| PostToolUse | `audit/log_actions` | Añade cada acción, con secretos redactados, a `.claude/audit/actions.jsonl`. |
| UserPromptSubmit | `block_secrets_in_prompt` | Rechaza un prompt que contiene un secreto antes de que llegue al modelo. |
| SubagentStop | `require_evidence` | Los agentes revisores y de pruebas no pueden cerrar sin una sección de evidencia (`fichero:línea`, comandos y resultados). |
| PreCompact | `preserve_state` | Indica al resumen de compactación que conserve fase, gates, decisiones y bloqueantes. |
| SessionEnd | `log_session_end` | Añade el cierre de sesión al registro de auditoría (no puede bloquear). |
| SessionStart | `load_context` | Inyecta fase, tier y módulos activos desde `.factory/state.json`. |
| Stop | `require_docs_updated` | No deja terminar si se tocó código sin tocar `docs/`. |
| Stop | `require_green_tests` | No deja terminar si el `test_command` configurado falla. |

Formatos de configuración verificados: [`docs/architecture/claude-code-formats.md`](../docs/architecture/claude-code-formats.md).
