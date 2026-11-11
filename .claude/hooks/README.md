# hooks

Código determinista (Python 3, ADR-0029) que Claude Code ejecuta en puntos concretos del trabajo de un agente. Existen porque una regla que se puede comprobar con un script no debe depender de que el modelo la recuerde.

## Cómo funcionan
- Cada hook lee un evento JSON por la entrada estándar y decide.
- **Código de salida 2: bloquea** la acción y el motivo va por la salida de error. **0: permite.**
- `UserPromptSubmit` bloquea con una respuesta JSON `{"decision": "block", "reason": "..."}`; `SessionEnd` no puede bloquear.
- Los hooks de seguridad fallan **cerrados**: si el evento es ilegible, bloquean.
- Un hook que bloquea gana siempre a una regla `allow` de los permisos.
- Se registran en [`../settings.json`](../settings.json) con la ruta `${CLAUDE_PROJECT_DIR}/.claude/hooks/...`.
- Utilidades comunes en `_lib.py` (lectura del evento, detección de secretos, rutas, contexto). Configuración por proyecto en `hooks-config.json`.

## Los 18 hooks
| Evento | Hook | Qué hace |
|---|---|---|
| PreToolUse | `pre-tool-use/block_secrets.py` | Rechaza escrituras con credenciales (claves AWS, tokens de GitHub o Slack, claves privadas, contraseñas literales) y ficheros sensibles (`.env`, `.pem`, `.tfstate`) |
| PreToolUse | `pre-tool-use/block_dangerous_commands.py` | Rechaza `rm -rf /` y similares, `git push --force`, `git reset --hard`, `--no-verify` en `git commit/push/merge`, `chmod 777`, `curl … \| sh`, `terraform apply` y `terraform destroy`, borrados amplios de `kubectl` y llamadas de AWS que crean, modifican o borran recursos (ADR-0004) |
| PreToolUse | `pre-tool-use/enforce_gate_approval.py` | Impide editar código si faltan registros de aprobación válidos para la fase actual; impide que un agente escriba `approvals/` o `.factory/state.json`, también desde la shell; una fase desconocida bloquea |
| PreToolUse | `pre-tool-use/block_forbidden_paths.py` | Protege `.git/`, `node_modules/`, `.terraform/`, `target/`, `*.tfstate`, `.claude/settings.json` y `.claude/hooks/` |
| PostToolUse | `post-tool-use/format_and_lint.py` | Ejecuta el formateador y el linter configurados por patrón de fichero; un fallo bloquea |
| PostToolUse | `post-tool-use/forbidden_deps.py` | Bloquea dependencias de `catalog/forbidden-libraries.yaml` (Lombok, entre otras) al editar `pom.xml`, `build.gradle`, `package.json`, `pnpm-lock.yaml` o `requirements*.txt` |
| PostToolUse | `post-tool-use/architecture_guard.py` | Bloquea imports de framework dentro de rutas `domain/` o `core/` de ficheros Java |
| PostToolUse | `post-tool-use/maturity_label_check.py` | Bloquea afirmaciones de que algo está verificado o listo en AWS real |
| PostToolUse | `post-tool-use/update_docs.py` | Anota qué ficheros cambiaron para exigir documentación al parar |
| PostToolUse | `post-tool-use/prompt_injection_guard.py` | Avisa cuando un resultado externo (web, fichero, herramienta) contiene instrucciones sospechosas |
| PostToolUse | `audit/log_actions.py` | Añade cada acción, con secretos redactados, a `.claude/audit/actions.jsonl` |
| UserPromptSubmit | `user-prompt-submit/block_secrets_in_prompt.py` | Rechaza un prompt que contiene un secreto antes de que llegue al modelo |
| SubagentStop | `subagent-stop/require_evidence.py` | Los agentes revisores y de pruebas no pueden cerrar sin evidencia (`fichero:línea`, comandos y resultados); la lista es configurable |
| PreCompact | `pre-compact/preserve_state.py` | Indica al resumen de compactación que conserve fase, gates con aprobación, decisiones y bloqueantes |
| SessionEnd | `session-end/log_session_end.py` | Añade el cierre de sesión al registro de auditoría |
| SessionStart | `session-start/load_context.py` | Inyecta fase, tier y módulos activos desde `.factory/state.json` |
| Stop | `stop/require_docs_updated.py` | No deja terminar si se tocó código sin tocar `docs/` |
| Stop | `stop/require_green_tests.py` | No deja terminar si el `test_command` configurado falla |

Los dos hooks de `Stop` y el de `SubagentStop` respetan `stop_hook_active` para no entrar en bucle.

## `hooks-config.json`
Configuración que cada proyecto adapta: `test_command` y `test_trigger_globs` (cuándo exigir pruebas en verde), `format` y `lint` (herramientas por patrón de fichero), `source_globs` (qué cuenta como código fuente; por defecto `*.java`, `*.ts`, `*.tsx`, `*.tf`, `*.py`, `pom.xml` y `*.yaml`) y `subagent_evidence.agents` (qué agentes deben cerrar con evidencia).

## Cómo añadir o cambiar un hook
1. Escribe el script en la carpeta de su evento y reutiliza `_lib.py`.
2. Regístralo en `settings.json`.
3. Añade sus pruebas en `tests/hooks/` y, si protege una regla de comportamiento, un caso en `tests/agent-evals/cases/hooks.yaml`.
4. Ejecuta `make check`.

Tests: [`tests/hooks/`](../../tests/hooks/README.md) y [`tests/agent-evals/`](../../tests/agent-evals/README.md). Formato de los eventos verificado en [`docs/architecture/claude-code-formats.md`](../../docs/architecture/claude-code-formats.md).
