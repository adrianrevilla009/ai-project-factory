# ADR-0007: Tier de resiliencia por defecto

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D7 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Warm standby (Tier 1); activo-activo solo por petición explícita.

## Por qué
Equilibrio coste/RTO para servicios de cara a cliente.

## Consecuencias
Catálogo en `catalog/resilience-tiers.yaml` (valores de partida a validar con negocio).
