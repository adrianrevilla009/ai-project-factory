---
name: parallel-work-and-worktrees
description: "Usar al repartir trabajo entre varias sesiones o agentes a la vez, para aislar ediciones con git worktree y evitar colisiones y merges rotos."
metadata:
  block: "31-agentic-engineering"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "hook"
---

# Trabajo en paralelo y worktrees

## Cuándo aplicar y cuándo no
- Aplica cuando dos o más sesiones o agentes editarán el mismo repositorio a la vez (por ejemplo, una oleada de skills).
- No aplica a tareas secuenciales ni a subagentes de solo lectura (exploración, revisión).

## Reglas
- **MUST** dar a cada trabajador de escritura un checkout aislado: un `git worktree` por rama.
- **MUST** repartir por propiedad de ficheros: cada agente escribe solo en su carpeta (p. ej. `.claude/skills/<name>/`).
- **MUST NOT** hacer que dos agentes editen el mismo fichero; ficheros compartidos (índices, inventarios) los actualiza un único integrador al final.
- **MUST NOT** saltarse gates por ir en paralelo: cada rama pasa sus aprobaciones (`approvals/gate-N.json`).
- **SHOULD** integrar en orden, con tests en verde tras cada merge.
- **SHOULD** limpiar worktrees terminados; no dejar ramas huérfanas.
- **SHOULD** limitar la paralelización al número de tareas realmente independientes (ver `cost-control`).

## Por qué
Dos sesiones sobre el mismo árbol se pisan: una lee un fichero a medias, la otra lo reescribe. Un worktree es un checkout separado con su propia rama y evita eso sin clonar el repositorio. Claude Code lo soporta con `claude --worktree <nombre>` (verificado 2026-11-07, https://code.claude.com/docs/en/common-workflows; requiere al menos un commit; detalles de limpieza y `.worktreeinclude` en https://code.claude.com/docs/en/worktrees.md). Hoy este directorio de la fábrica no es un repositorio git, así que el aislamiento por worktree solo aplica a proyectos generados con git; aquí la separación se logra por propiedad de carpetas.

## Ejemplos
### Mal
```text
Agente A y agente B editan a la vez catalog/skills-inventory.yaml y docs/skills-index.md.
```
### Bien
```bash
git worktree add ../proj-feature-auth -b feature/auth
git worktree add ../proj-feature-billing -b feature/billing
claude --worktree feature-search     # alternativa gestionada por Claude Code
git worktree list
git worktree remove ../proj-feature-auth   # al terminar
```
Reparto por propiedad:
```text
agente 1 -> .claude/skills/mcp-governance/**
agente 2 -> .claude/skills/agent-evals/**
integrador (humano o tech-lead) -> catalog/skills-inventory.yaml, docs/skills-index.md
```

## Criterios de decisión y trampas
### Cómo decidir
- Paraleliza tareas independientes con copias de trabajo separadas para que no se pisen; fusiona con revisión y comprobaciones.
- Si las tareas dependen entre sí, no las paralelices.
### Trampas frecuentes
- Agentes editando los mismos ficheros a la vez.
- Fusiones sin revisión.
- Tareas dependientes lanzadas en paralelo.
- Más paralelismo que capacidad de revisar.
- Sin límite de agentes simultáneos.
### Evidencia
- Cada tarea paralela tiene su rama y su revisión, y no hay conflictos sin resolver.

## Checklist de revisión
- [ ] Cada trabajador de escritura tiene rama y worktree propios, o carpeta exclusiva.
- [ ] No hay ficheros editados por más de un agente.
- [ ] Los ficheros compartidos los toca un solo integrador.
- [ ] Tests en verde tras cada integración.
- [ ] Worktrees y ramas terminados eliminados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Los agentes no pueden escribir aprobaciones ni estado de gates | 1 | `.claude/hooks/pre-tool-use/enforce_gate_approval.py` (tests en `tests/hooks/test_hooks.py`) |
| No terminar con tests rojos tras integrar | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Rutas prohibidas por agente | 2 | `.claude/hooks/pre-tool-use/block_forbidden_paths.py` |
| Reparto y orden de integración | 3 | agente `tech-lead` (lista este skill en su ficha) |

## Relacionados, fuentes y mantenimiento
- Relacionados: `handoff-artifacts-between-agents`, `cost-control`, `gate-protocol`.
- Fuentes: https://code.claude.com/docs/en/common-workflows (consultada 2026-11-07); documentación de `git worktree`.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
