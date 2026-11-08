# ADR-0028: Estructura plana de skills

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión adicional tomada durante la Oleada 0.

## Decisión
Los skills viven en `.claude/skills/<nombre>/SKILL.md` (plano). El bloque (01–31) y el nivel T1/T2/T3 se declaran en `metadata`.

## Por qué
El brief sugiere agrupar en carpetas por bloque (`.claude/skills/31-agentic-engineering/`), pero la documentación de Claude Code espera `.claude/skills/<nombre>/SKILL.md` para el descubrimiento. Comprobar si se descubren skills anidados; mientras tanto se usa la estructura plana verificada.

## Consecuencias
Un índice por bloque se genera desde `metadata.block`. Desviación consciente del brief §5/§12.4.
