# ADR-0024: Un único agente de dominio adaptativo

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D24 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
`domain-analyst` lee un perfil de dominio por proyecto; no hay agentes por sector.

## Por qué
Evitar contenido sectorial sin revisión experta (riesgo, no valor).

## Consecuencias
Perfil validado por experto de negocio en Gate 0.
