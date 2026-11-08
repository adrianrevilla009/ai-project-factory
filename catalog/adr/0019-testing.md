# ADR-0019: Testing

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D19 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Testcontainers, Pact (+Broker), JMeter, Chaos Monkey for Spring Boot, Chaos Mesh, Toxiproxy, WireMock, ArchUnit, PIT; LocalStack para lo emulable, solo con plan de pago y ADR propio: desde 2026-03-23 no hay edición Community y el plan gratuito es no comercial (verificado 2026-11-08); mientras tanto, emuladores sin cuenta (DynamoDB Local, ElasticMQ, MinIO).

## Por qué
Pirámide de pruebas con dependencias reales.

## Consecuencias
Testcontainers requiere acceso a Docker (ver ADR-0030).
