# Cómo usar la fábrica

Para quien va a crear un proyecto con ella o a mantenerla.

## Qué necesitas
- Claude Code y esta carpeta clonada. Para mantener la fábrica, Python 3 (`make setup`).
- Alguien que firme los gates: sin una persona que apruebe, el flujo no avanza (por diseño).

## Crear un proyecto
1. **Abre Claude Code en la fábrica** y lanza `/project-init <ruta-destino> <nombre>`. El agente crea la carpeta destino, entrevista a quien corresponda sobre capacidades y prepara el `.claude/` y el `CLAUDE.md` del proyecto con los hooks de seguridad.
2. **Una persona crea** `.factory/state.json` y la carpeta `approvals/` en el destino: los agentes no pueden escribirlas, a propósito.
3. **Abre Claude Code en el proyecto destino** y sigue con `/project-discover`. El flujo es: descubrimiento del dominio y la normativa, plan, implementación, pull request, release y revisión cloud. Al final de cada fase el agente **se detiene** y presenta evidencia.
4. **Revisa y aprueba** cada gate (0–5) creando `approvals/gate-N.json` con el esquema de `gates/approval-record.schema.json`. El hook de gates impide editar código si faltan aprobaciones válidas.
5. **Cierra** con `/project-retro` y `/lessons-capture`.

El detalle de fases y comandos está en [`project-lifecycle.md`](operating-model/project-lifecycle.md); quién aprueba cada gate, en [`RACI.md`](operating-model/RACI.md).

## Qué esperar (y qué no)
- Todo el contenido normativo (RGPD, AI Act, accesibilidad…) sale como **borrador por confirmar** con fuente oficial y una persona de legal o cumplimiento.
- La infraestructura AWS se escribe y se valida de forma estática, pero **nunca se despliega**: la etiqueta correcta es «preparado para AWS, no verificado en real».
- Cuando un agente no puede comprobar un dato, lo declara «no comprobado» en vez de inventarlo.

## Mantener la fábrica
| Quiero… | Hago… |
|---|---|
| Añadir o cambiar una skill | Copia `.claude/skills/_template/`, sigue `docs/skill-writing-brief.md` y ejecuta `make index` y `make check` |
| Tomar una decisión de arquitectura | Escribe un ADR en `catalog/adr/` y añádelo a su tabla |
| Añadir un servidor MCP | Una entrada en `catalog/mcp-servers.yaml` (versión fijada, credenciales por variable) y un PR |
| Añadir un hook | Un script en `.claude/hooks/<evento>/`, su registro en `settings.json` y tests en `tests/hooks/` |
| Ver qué skills hay | [`skills-index.md`](skills-index.md) y los catálogos de [`knowledge/`](../knowledge/README.md) |

## Dónde mirar si algo falla
- `make validate` indica qué skill, catálogo o enlace está roto.
- `.claude/audit/actions.jsonl` en el proyecto registra las acciones del agente, con secretos redactados.
- Un bloqueo de hook explica el motivo en pantalla; si parece un falso positivo, no lo saltes: abre un PR para ajustarlo.
