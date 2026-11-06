---
name: claude-md-authoring
description: Usar al escribir o editar un CLAUDE.md (de la fábrica o de un proyecto generado) para que sea corto y efectivo.
metadata:
  block: "31-agentic-engineering"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-06"
  enforcement: "policy"
---

# Autoría de CLAUDE.md

## Cuándo aplicar y cuándo no
- Aplica a `CLAUDE.md` raíz y de subdirectorios.
- No aplica a skills (detalle y ejemplos van allí).

## Reglas
- **MUST** ser corto (objetivo < 80 líneas): solo reglas que nunca deben olvidarse.
- **MUST** enlazar a detalle (ADRs, skills, docs) en vez de copiarlo.
- **MUST** incluir comandos de build/test/validate reales y verificados.
- **MUST NOT** incluir secretos, versiones sin verificar ni normativa de memoria.
- **SHOULD** redactar reglas verificables ("MUST NOT usar Lombok"), no aspiraciones.
- **SHOULD** mover a hooks/policies toda regla comprobable por script.

## Por qué
CLAUDE.md se carga siempre: cada línea cuesta contexto en cada sesión. Lo que es largo o procedimental pertenece a un skill que se carga bajo demanda.

## Ejemplos
### Mal
Un CLAUDE.md de 600 líneas con guía completa de JPA.
### Bien
Diez reglas, tabla de comandos y enlaces a `.claude/skills/`.

## Checklist de revisión
- [ ] < 80 líneas.
- [ ] Cada comando documentado funciona.
- [ ] Sin duplicar contenido de skills.
- [ ] Idioma: español para prosa, inglés para identificadores.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador: límite de líneas de CLAUDE.md | 1 | `factory/validators/skill_structure.py` (aviso) |
| Revisión humana | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `skill-authoring-guide`, `context-budgeting`.
- Fuentes: https://code.claude.com/docs/en/ (memoria/CLAUDE.md) — TODO-VERIFY ruta exacta.
- Dueño: factory-owner · Última revisión: 2026-11-06 · Nivel: T1
