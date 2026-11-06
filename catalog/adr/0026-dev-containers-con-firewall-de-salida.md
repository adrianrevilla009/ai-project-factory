# ADR-0026: Dev containers con firewall de salida

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D26 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Dev containers con allowlist de red de salida.

## Por qué
Un agente con red abierta y credenciales es un riesgo real.

## Consecuencias
Acceso a Docker para Testcontainers: ver ADR-0030.
