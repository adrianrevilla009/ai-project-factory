# ADR-0008: IaC con Terraform

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D8 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Terraform con módulos y entornos por cuenta.

## Por qué
Estándar de facto, ecosistema de escaneo (Checkov/Trivy/OPA) y validación estática.

## Consecuencias
Versiones de proveedores fijadas; comprobar versión de Terraform y licencia vigente.
