# ADR-0005: Kubernetes local en lugar de Docker Compose

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D5 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Entorno local sobre Kubernetes (kind o k3d; ver ADR-0034), no Docker Compose.

## Por qué
Paridad con EKS/GitOps/Istio y manifiestos reutilizables.

## Consecuencias
Perfiles mínimo/completo con presupuesto de recursos documentado.
