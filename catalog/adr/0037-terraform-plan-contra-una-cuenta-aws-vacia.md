# ADR-0037: `terraform plan` contra una cuenta AWS vacía

- **Estado:** aceptado
- **Fecha:** 2026-11-07

## Contexto
Decisión que el brief dejaba abierta (§3). El dueño la cerró el 2026-11-09 aceptando la opción indicada en «Decisión».

## Opciones
- No (por defecto): coherente con D4.
- Sí, opcional y desactivado por defecto, con credenciales de solo lectura.

## Decisión
NO. Ningún `terraform plan` contra cuentas AWS (coherente con D4).

## Consecuencias
Por determinar al decidir.
