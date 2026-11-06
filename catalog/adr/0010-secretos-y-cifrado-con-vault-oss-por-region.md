# ADR-0010: Secretos y cifrado con Vault OSS por región

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D10 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Vault de código abierto, un clúster independiente por región, sin replicación Enterprise. Variante Enterprise solo como documentación opcional.

## Por qué
Evitar licencias de pago (D16) y mantener independencia de fallo por región.

## Consecuencias
Transit no comparte material de claves entre regiones: datos leídos desde ambas regiones usan claves multi-región de KMS (cifrado de sobre). Ver ADR-0031 (licencia BUSL y OpenBao).
