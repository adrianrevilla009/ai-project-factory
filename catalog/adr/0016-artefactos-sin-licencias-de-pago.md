# ADR-0016: Artefactos sin licencias de pago

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D16 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Puerto neutro `artifact-repository-port`: Harbor + repositorio Maven/npm gratuito (ver ADR-0035). Artifactory como adaptador opcional.

## Por qué
Evitar dependencia de producto de pago.

## Consecuencias
Imágenes de runtime se despliegan desde ECR, no desde Harbor.
