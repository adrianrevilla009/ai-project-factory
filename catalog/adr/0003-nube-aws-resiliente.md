# ADR-0003: Nube AWS resiliente

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D3 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
AWS diseñada resiliente: multi-AZ, multi-región, DR.

## Por qué
Requisito de negocio de resiliencia; AWS es el destino objetivo.

## Consecuencias
Todo el diseño de infra contempla dos regiones; ver ADR-0004 y ADR-0006.
