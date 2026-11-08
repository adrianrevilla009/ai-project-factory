# ADR-0028: Estructura plana de skills

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión adicional tomada durante la Oleada 0.

## Decisión
Los skills viven en `.claude/skills/<nombre>/SKILL.md` (plano). El bloque (01–31) y el nivel T1/T2/T3 se declaran en `metadata`.

## Por qué
El brief sugiere agrupar en carpetas por bloque (`.claude/skills/31-agentic-engineering/`), pero la documentación de Claude Code espera `.claude/skills/<nombre>/SKILL.md` para el descubrimiento. Verificado el 2026-11-08 en https://code.claude.com/docs/en/skills: un skill en una subcarpeta (`.claude/skills/grupo/nombre/`) **no se descubre**; solo se cargan los que están directamente en `.claude/skills/<nombre>/`. La estructura plana es, por tanto, obligatoria y no una preferencia.

## Consecuencias
Un índice por bloque se genera desde `metadata.block`. Desviación consciente del brief §5/§12.4.
