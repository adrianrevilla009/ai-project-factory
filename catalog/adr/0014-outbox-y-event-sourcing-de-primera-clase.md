# ADR-0014: Outbox y Event Sourcing de primera clase

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D14 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Ambos son patrones de primera clase, con reglas de oro en brief §4.5.

## Por qué
Atomicidad dentro de una BD (outbox) o eventos como fuente de verdad (ES).

## Consecuencias
Event sourcing ≠ auditoría; skill de decisión obligatorio. DynamoDB Global Tables: región de escritura por agregado (TODO-VERIFY consistencia fuerte multi-región).
