# ADR-0002: Build con Maven multi-módulo

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D2 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Maven multi-módulo con parent POM y BOM corporativo.

## Por qué
Reproducibilidad, control central de versiones y reglas Enforcer verificables.

## Consecuencias
Versiones de dependencias solo en el BOM; `forbidden-libraries` se aplica con Enforcer.
