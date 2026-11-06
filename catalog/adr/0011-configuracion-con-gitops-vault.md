# ADR-0011: Configuración con GitOps + Vault

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D11 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
GitOps + Vault por defecto; Spring Cloud Config Server como módulo opcional con guía de decisión.

## Por qué
Menos componentes y auditoría vía Git.

## Consecuencias
Existe skill `spring-cloud-config-module` (opcional).
