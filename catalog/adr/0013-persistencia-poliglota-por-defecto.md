# ADR-0013: Persistencia políglota por defecto

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión D13 del brief de la fábrica (`docs/FACTORY_BRIEF.md` §3).

## Decisión
Aurora PostgreSQL (estado) + DynamoDB (event store/clave-valor); OpenSearch y Redis como módulos.

## Por qué
Cada dato en el almacén adecuado, con una única fuente de verdad por agregado.

## Consecuencias
Coste operativo mayor (skill `polyglot-operations-cost`). Prohibida la doble escritura Postgres+NoSQL.
