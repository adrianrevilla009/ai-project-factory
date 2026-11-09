---
name: cost-control
description: "Usar al planificar sesiones largas, subagentes en paralelo o cargas masivas de contexto para acotar el consumo de tokens y el coste del uso de agentes."
metadata:
  block: "31-agentic-engineering"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Control de coste de agentes

## Cuándo aplicar y cuándo no
- Aplica al diseñar flujos con varios agentes, bucles automáticos, ejecuciones no interactivas y skills que cargan mucho contexto.
- No aplica al coste de infraestructura cloud (ver `finops`; la fábrica no despliega nada) ni a decisiones de precio de productos.

## Reglas
- **MUST** definir un tope explícito por tarea automática: número máximo de iteraciones y condición de parada.
- **MUST** delegar exploraciones largas a un subagente para que solo vuelva el resumen al contexto principal.
- **MUST** pedir artefactos concretos (ruta + resumen), no volcar ficheros enteros entre agentes.
- **MUST NOT** lanzar subagentes en paralelo sin necesidad: cada uno consume contexto propio.
- **SHOULD** mantener `CLAUDE.md` y las `description` de skills cortas; la descripción se paga en cada sesión.
- **SHOULD** elegir el modelo según la tarea (campo `model` del agente): tareas mecánicas con modelo menor. Comprobar nombres y precios vigentes; no se fijan aquí.
- **SHOULD** limitar la salida de herramientas (`head`, filtros) antes de que entre al contexto.
- **SHOULD** revisar el consumo tras cada oleada de trabajo y anotar las causas de picos.

## Por qué
El coste crece con el contexto acumulado y con el número de turnos, no con el valor entregado. Un bucle sin tope o un `cat` de un log de 20 000 líneas cuestan igual que trabajo útil. Los límites deben ser explícitos y estar fuera del criterio del propio agente. Cifras y planes de precios cambian: consultar la documentación oficial vigente.

## Ejemplos
### Mal
```text
"Revisa todo el repositorio y arregla lo que veas." (sin tope, sin criterio de fin, contexto completo)
```
### Bien
```text
Tarea: migrar 12 clases a records. Tope: 3 intentos por clase.
Parada: tests en verde o fallo reportado tras el tercer intento.
Exploración previa -> subagente, devuelve solo lista de rutas.
```
Salida acotada antes de entrar al contexto:
```bash
mvn -q test 2>&1 | tail -n 40
grep -c "ERROR" build.log
```
Agente con alcance mínimo (frontmatter real, campos `name`, `description`, `tools`):
```yaml
---
name: example-reader
description: "Usar para localizar ficheros; devuelve solo rutas."
tools: Read, Grep, Glob
---
```

## Checklist de revisión
- [ ] Todo bucle automático tiene tope de iteraciones y condición de parada.
- [ ] Las exploraciones grandes van a subagentes con resumen acotado.
- [ ] Las salidas de herramientas se filtran antes de leerlas.
- [ ] El paralelismo está justificado por independencia real de las tareas.
- [ ] No se afirman precios ni límites sin fuente.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Registro de acciones para medir qué se ejecuta | 2 | `.claude/hooks/audit/log_actions.py` (escribe `.claude/audit/actions.jsonl`) |
| Revisión del diseño del flujo | 3 | agente `finops-analyst` (coste cloud) y `tech-lead` (coste de agentes) |
| Topes y presupuesto automáticos por tarea | - | pendiente: sin hook de presupuesto; revisión humana |

## Relacionados, fuentes y mantenimiento
- Relacionados: `parallel-work-and-worktrees`, `handoff-artifacts-between-agents`, `context-budgeting`, `finops`.
- Fuentes: https://code.claude.com/docs/en/common-workflows (delegar en subagentes, consultada 2026-11-07).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
