# ADR-0019: Testing

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D19 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Testcontainers, Pact (+Broker), JMeter, Chaos Monkey for Spring Boot, Chaos Mesh, Toxiproxy, WireMock, ArchUnit, PIT; LocalStack para lo emulable.

## Por qué
Pirámide de pruebas con dependencias reales.

## Consecuencias
Testcontainers requiere acceso a Docker (ver ADR-0030).
