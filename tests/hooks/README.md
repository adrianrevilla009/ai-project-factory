# hooks

Las pruebas de los hooks de [`.claude/hooks/`](../../.claude/hooks/README.md). Cada hook se prueba **como en producción**: se lanza como un subproceso, se le pasa un evento JSON por la entrada estándar y se comprueba el código de salida y lo que imprime.

| Fichero | Qué cubre |
|---|---|
| `test_hooks.py` | Los hooks de `PreToolUse`: bloqueo de secretos, de comandos peligrosos y de rutas protegidas, y el cumplimiento de los gates (aprobaciones válidas, fases, intentos de forzar un registro desde la shell) |
| `test_hooks_extra.py` | Los hooks de `SessionStart`, `PostToolUse` y `Stop` y la auditoría: contexto de sesión, dependencias prohibidas, arquitectura, afirmaciones de madurez, documentación y pruebas en verde al parar |
| `test_hooks_events.py` | Los hooks de `UserPromptSubmit`, `SubagentStop`, `PreCompact` y `SessionEnd`, y que todos queden registrados en `settings.json` |

## Qué se comprueba siempre
- El caso que **debe bloquearse** (código de salida 2) y el que **debe permitirse** (0).
- Que los hooks de seguridad fallan cerrados ante una entrada ilegible.
- Que los hooks de parada no entran en bucle (`stop_hook_active`).

Los casos de comportamiento de más alto nivel están en [`../agent-evals/`](../agent-evals/README.md).
