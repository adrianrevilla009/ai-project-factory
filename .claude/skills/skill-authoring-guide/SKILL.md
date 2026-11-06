---
name: skill-authoring-guide
description: Usar al crear o revisar un skill de la fábrica; define anatomía obligatoria, niveles T1/T2/T3 y reglas de enforcement.
metadata:
  block: "31-agentic-engineering"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-06"
  enforcement: "policy"
---

# Guía de autoría de skills

## Cuándo aplicar y cuándo no
- Aplica al crear, modificar o revisar cualquier carpeta en `.claude/skills/`.
- No aplica a `CLAUDE.md` (ver `claude-md-authoring`) ni a reglas que puedan ser un script puro (van a hooks/policies).

## Reglas
- **MUST** copiar `.claude/skills/_template/SKILL.md` y rellenar las 7 secciones de la anatomía: cuándo aplicar, reglas, por qué, ejemplos bueno/malo, checklist, enforcement, relacionados/fuentes.
- **MUST** poner una `description` corta (una frase, < 200 caracteres) que diga *cuándo* cargar el skill.
- **MUST** declarar en `metadata`: `block`, `tier`, `owner`, `last_reviewed`, `enforcement`.
- **MUST** indicar en *Enforcement* un mecanismo real (artefacto con ruta) o declarar "revisión humana".
- **MUST** citar fuentes oficiales con fecha; lo no verificable lleva `TODO-VERIFY`.
- **MUST NOT** afirmar que algo funciona en AWS real (ver `verify-before-asserting`).
- **SHOULD** usar código real de `reference-app/` en los ejemplos cuando exista.
- **SHOULD** mantener `SKILL.md` < 400 líneas; el detalle va a `references/` y `examples/`.
- **MUST NOT** copiar contenido de repositorios externos sin revisar su licencia.

## Por qué
Una descripción larga o ambigua hace que el agente cargue skills irrelevantes y gaste contexto. Un skill sin enforcement es una sugerencia: se pudre. Las fechas de revisión permiten detectar caducidad (`skill-review`).

## Ejemplos
### Mal
```yaml
description: Este skill contiene todo lo que hay que saber sobre bases de datos, transacciones, índices y rendimiento en distintos escenarios…
```
### Bien
```yaml
description: Usar al diseñar o revisar consultas JPA para evitar el problema N+1.
```

## Checklist de revisión
- [ ] Las 7 secciones existen y no son relleno.
- [ ] `description` corta y accionable.
- [ ] Metadatos completos y fecha de revisión reciente.
- [ ] Enforcement apunta a un artefacto existente.
- [ ] Ejemplos compilan o proceden de la app de referencia.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador de estructura de skills | 1 | `factory/validators/skill_structure.py` (`make validate`) |
| Revisión humana de contenido | 4 | PR |

## Relacionados, fuentes y mantenimiento
- Relacionados: `verify-before-asserting`, `claude-md-authoring`, `n-plus-one` (ejemplo completo).
- Fuentes: https://code.claude.com/docs/en/skills.md (verificado 2026-11-06).
- Dueño: factory-owner · Última revisión: 2026-11-06 · Nivel: T1
