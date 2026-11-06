# ADR-0012: Identidad con Keycloak

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D12 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Keycloak; BD en Aurora Global; en failover se asume reinicio de sesión.

## Por qué
Sin licencia de pago, estándar OIDC.

## Consecuencias
Runbook de failover documenta el reinicio de sesión.
