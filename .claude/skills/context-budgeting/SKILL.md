---
name: context-budgeting
description: "Usar cuando una sesión se alarga, el contexto se llena o al decidir qué cargar (CLAUDE.md, skills, MCP, ficheros): presupuesto de contexto y compactación."
metadata:
  block: "31-agentic-engineering"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "hook"
---

# Presupuesto de contexto

## Cuándo aplicar y cuándo no
- Aplica a sesiones largas, a tareas que leen mucho (logs, repos grandes) y al diseñar qué va en `CLAUDE.md`, skills o MCP.
- No aplica a consultas puntuales de pocos pasos.

## Reglas
- **MUST** mantener `CLAUDE.md` corto (límite de la fábrica: 80 líneas) y mover el detalle a skills, que se cargan bajo demanda (`claude-md-authoring`).
- **MUST** delegar a un subagente las lecturas voluminosas (logs, búsquedas amplias, ejecución de tests) y recibir solo el resumen (`subagent-design`).
- **MUST** limpiar (`/clear`) al cambiar a una tarea no relacionada; antes, dejar el estado en un fichero (`handoff-artifacts-between-agents`).
- **SHOULD** compactar con instrucciones de qué conservar (`/compact` + foco: decisiones, rutas, tests fallidos) antes de que se autocompacte.
- **SHOULD** leer por rangos (`offset`/`limit`) y no ficheros enteros cuando se sabe qué parte hace falta.
- **SHOULD** filtrar la salida con scripts/hooks (p. ej. solo líneas `ERROR`) en lugar de leer logs completos.
- **SHOULD** revisar con `/context` qué ocupa espacio (MCP, memoria, skills) y desactivar lo no usado.
- **MUST NOT** pegar volcados completos (stack traces enteros, JSON de 10 000 líneas) cuando basta un extracto con la ruta del original.
- **MUST NOT** guardar decisiones solo en la conversación: tras compactar o limpiar se pierden; van a ADR/ficheros de fase.

## Por qué
Claude Code reenvía la conversación completa en cada petición; contexto largo = más coste, más latencia y peor atención a las reglas importantes. Los skills cargan bajo demanda, `CLAUDE.md` siempre. La recomendación oficial de mantener `CLAUDE.md` bajo ~200 líneas y las prácticas de `/clear`, `/compact`, `/context` y delegación a subagentes están en https://code.claude.com/docs/en/costs (2026-11-07); la fábrica es más estricta (80). Los nombres exactos de comandos pueden cambiar entre versiones: se consultan en la documentación de la versión instalada.

## Ejemplos
### Mal
```text
Lee todo target/surefire-reports/ y dime qué falla.   # miles de líneas en el contexto principal
```
### Bien
```text
Delega en un subagente: ejecuta `make test`, y devuelve solo los tests fallidos
(nombre, ruta:línea, primera línea del error). Máximo 15 líneas.
```
### Instrucciones de compactación
```text
/compact Conserva: decisiones de diseño, ficheros tocados, tests pendientes y el gate actual.
```
### Hook que reduce lo que entra (esquema)
```python
# PostToolUse/PreToolUse: devolver solo las líneas relevantes de un log
import re, sys
lines = [l for l in sys.stdin if re.search(r"ERROR|FAIL", l)]
print("".join(lines[:100]))
```

## Checklist de revisión
- [ ] `CLAUDE.md` <= 80 líneas; el detalle está en skills.
- [ ] Las lecturas pesadas se delegaron y volvió un resumen.
- [ ] El estado importante está en ficheros, no solo en la conversación.
- [ ] No hay servidores MCP activos sin uso.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de longitud de `CLAUDE.md` (<= 80) y de skills (< 400 líneas) | 1 | `factory/validators/skill_structure.py` |
| Hook `SessionStart` que carga solo un resumen de fase/módulos | 1 | `.claude/hooks/session-start/load_context.py` |
| Hook de filtrado de salidas voluminosas | 2 | pendiente |
| Higiene de sesión (`/clear`, `/compact`) | 4 | revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `claude-md-authoring`, `subagent-design`, `cost-control`, `handoff-artifacts-between-agents`.
- Fuentes: https://code.claude.com/docs/en/costs (consultado 2026-11-07).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
