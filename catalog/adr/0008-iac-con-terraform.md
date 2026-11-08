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
Versiones de proveedores fijadas; Terraform se publica bajo BUSL 1.1 (licenciante: IBM desde el 2025-02-27; verificado el 2026-11-08); no es de pago para este uso, pero un revisor legal debe confirmarlo. OpenTofu (MPL 2.0) queda como alternativa.
