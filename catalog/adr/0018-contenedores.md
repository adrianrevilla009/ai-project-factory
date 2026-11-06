# ADR-0018: Contenedores

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D18 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Docker multi-stage, imágenes mínimas, no-root, FS de solo lectura.

## Por qué
Reduce superficie de ataque.

## Consecuencias
Políticas Kyverno/OPA lo hacen cumplir.
