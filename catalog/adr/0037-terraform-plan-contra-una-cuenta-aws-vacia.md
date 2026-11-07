# ADR-0037: `terraform plan` contra una cuenta AWS vacía

- **Estado:** aceptado (por defecto; revisable por el dueño)
- **Fecha:** 2026-11-07

## Contexto
Decisión abierta del brief (§3). No se inventa una respuesta; requiere confirmación humana.

## Opciones
- No (por defecto): coherente con D4.
- Sí, opcional y desactivado por defecto, con credenciales de solo lectura.

## Decisión
NO. Ningún `terraform plan` contra cuentas AWS (coherente con D4).

## Consecuencias
Por determinar al decidir.
