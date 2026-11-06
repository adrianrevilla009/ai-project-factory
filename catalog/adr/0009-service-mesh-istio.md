# ADR-0009: Service mesh Istio

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D9 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Istio; sidecar vs ambient se decide en ADR-0032.

## Por qué
mTLS, autorización y gestión de tráfico declarativas.

## Consecuencias
No duplicar reintentos entre mesh y aplicación (skill `mesh-vs-app-resilience`).
