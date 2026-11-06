# ADR-0023: Políticas

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D23 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
OPA/Conftest + Kyverno; Checkov/Trivy para IaC; Semgrep para código.

## Por qué
Políticas ejecutables que bloquean el CI.

## Consecuencias
Cada skill declara su enforcement.
