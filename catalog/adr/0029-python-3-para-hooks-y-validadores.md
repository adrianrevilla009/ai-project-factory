# ADR-0029: Python 3 para hooks y validadores

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión adicional tomada durante la Oleada 0.

## Decisión
Hooks y validadores de la fábrica se escriben en Python 3 (stdlib + pyyaml + jsonschema) con pytest.

## Por qué
Decisión del dueño (2026-11-06). Más robusto que Bash para parsear JSON y fácil de testear.

## Consecuencias
Entorno de desarrollo base: Python 3.10 detectado localmente; el código debe ser compatible con 3.10+.
