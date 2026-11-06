# ADR-0017: Escaneo y SBOM

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D17 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Trivy + Grype + OWASP Dependency-Check; CycloneDX + Dependency-Track. Xray opcional.

## Por qué
Cobertura redundante con herramientas libres.

## Consecuencias
Falsos positivos gestionados con VEX.
