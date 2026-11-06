# ADR-0021: GitOps y entrega progresiva

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D21 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Argo CD + Argo Rollouts; Flux y Spinnaker como T3.

## Por qué
Despliegue declarativo y análisis de canarios.

## Consecuencias
ApplicationSets multi-clúster para DR.
