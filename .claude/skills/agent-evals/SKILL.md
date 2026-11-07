---
name: agent-evals
description: "Usar al diseñar o ejecutar evaluaciones que comprueben que los agentes y hooks respetan reglas y gates (tests/agent-evals, tests/hooks)."
metadata:
  block: "31-agentic-engineering"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "hook"
---

# Evals de agentes

## Cuándo aplicar y cuándo no
- Aplica al cambiar un agente de `.claude/agents/`, un skill, un hook o un prompt, y al añadir casos a `tests/agent-evals`.
- No aplica a tests unitarios de código Java del proyecto generado (ver skills de testing) ni a evaluar calidad de modelos en general.

## Reglas
- **MUST** separar lo determinista de lo probabilístico: las reglas duras se prueban sobre hooks (`tests/hooks`), no pidiendo al modelo que se porte bien.
- **MUST** escribir cada caso como entrada fija, comportamiento esperado y criterio de aprobación comprobable por script.
- **MUST** incluir casos negativos: intento de escribir en `approvals/`, comando peligroso, secreto en un fichero, salto de gate.
- **MUST** reportar tasa de paso sobre N ejecuciones para casos con LLM; un solo verde no prueba nada.
- **MUST NOT** usar como juez al mismo agente evaluado ni dejar que el evaluado vea el criterio.
- **SHOULD** guardar la traza (herramientas llamadas) y evaluar la trayectoria, no solo la respuesta final.
- **SHOULD** versionar el conjunto de casos y registrar el modelo usado; los umbrales cambian con el modelo (TODO-VERIFY política de versiones de modelo).
- **SHOULD** crecer el conjunto con cada incidente: un fallo real se convierte en un caso.

## Por qué
Los agentes fallan de forma no determinista y un prompt cambiado puede romper una regla sin que nadie lo vea. La fábrica ya aplica sus gates como código (hook `enforce_gate_approval.py`): eso se prueba con pytest, barato y estable. Lo que queda para evals con LLM es lo que un hook no puede ver: si el agente elige el skill correcto o respeta su rol. El agente `eval-engineer` es el responsable de este trabajo.

## Ejemplos
### Mal
```text
Prompt: "Recuerda no tocar approvals/". Resultado: el agente respondió bien una vez. Marcado como OK.
```
### Bien
Caso determinista (patrón de `tests/hooks/test_hooks.py`; helper ilustrativo):
```python
def test_agents_cannot_write_approvals(tmp_path):
    result = run_hook("pre-tool-use/enforce_gate_approval.py",
                      tool="Write", path="approvals/gate-1.json", cwd=tmp_path)
    assert result.returncode == 2   # exit 2 = bloqueo
```
Caso con LLM (formato propuesto, pendiente de implementar en `tests/agent-evals/`):
```yaml
id: backend-java-respects-no-lombok
agent: backend-java
input: "Añade un getter a la entidad Order"
pass_if:
  - no_file_matches: "import lombok"
runs: 5
min_pass_rate: 1.0
```

## Checklist de revisión
- [ ] Cada regla dura tiene test en `tests/hooks` antes que eval con LLM.
- [ ] Hay casos negativos y al menos uno por gate afectado.
- [ ] Los casos con LLM declaran `runs` y umbral.
- [ ] El criterio se evalúa por script, sin depender de la opinión del propio agente.
- [ ] Un incidente reciente tiene su caso de regresión.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Tests de hooks (bloqueo, fail-closed, gates) | 1 | `tests/hooks/test_hooks.py`, `tests/hooks/test_hooks_extra.py` |
| Hook de parada: no terminar con tests rojos | 2 | `.claude/hooks/stop/require_green_tests.py` (comando en `.claude/hooks/hooks-config.json`) |
| Casos de agentes con LLM | 3 | `tests/agent-evals/` (estructura creada, contenido pendiente) |
| Diseño y revisión de evals | 3 | agente `eval-engineer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `mcp-governance`, `cost-control`, `verify-before-asserting`, `handoff-artifacts-between-agents`.
- Fuentes: `tests/hooks/README.md`, `.claude/agents/quality/eval-engineer.md`; salida de hooks (exit 2) según `docs/architecture/claude-code-formats.md`.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
