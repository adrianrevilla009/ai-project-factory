# ADR-0030: Acceso a Docker en el dev container

- **Estado:** aceptado
- **Fecha:** 2026-11-06

## Contexto
Decisión adicional tomada durante la Oleada 0.

## Decisión
El dev container incluye acceso a Docker para Testcontainers y kind, mediante socket del host montado.

## Por qué
Decisión del dueño (2026-11-06): añadirlo ahora. Implicación de seguridad: el socket de Docker equivale a root en el host; mitigaciones: firewall de salida por allowlist, sin credenciales cloud en el contenedor, y alternativa documentada (Docker-in-Docker rootless o Sysbox) para revisar en la Oleada 3. Riesgo de §13 aceptado y documentado.

## Consecuencias
TODO-VERIFY si Docker rootless es viable para kind + Testcontainers.
