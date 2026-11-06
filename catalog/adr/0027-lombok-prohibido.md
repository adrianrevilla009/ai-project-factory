# ADR-0027: Lombok prohibido

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D27 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Prohibido; usar records y builders explícitos.

## Por qué
Código explícito, mejor soporte de herramientas y menos magia.

## Consecuencias
Enforcer + hook `forbidden-deps` lo bloquean.
