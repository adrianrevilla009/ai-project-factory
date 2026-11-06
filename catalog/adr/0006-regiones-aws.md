# ADR-0006: Regiones AWS

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D6 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
eu-west-1 (principal) y eu-central-1 (secundaria), parametrizadas en Terraform.

## Por qué
Residencia UE y proximidad entre regiones.

## Consecuencias
TODO-VERIFY disponibilidad de todos los servicios usados en ambas regiones antes de la Oleada 3.
