# ADR-0033: CNI en EKS: VPC CNI vs Cilium

- **Estado:** aceptado
- **Fecha:** 2026-11-07

## Contexto
Decisión que el brief dejaba abierta (§3). El dueño la cerró el 2026-11-09 aceptando la opción indicada en «Decisión».

## Opciones
- VPC CNI: nativo AWS.
- Cilium: más funciones; verificar compatibilidad con Istio.

## Decisión
VPC CNI por defecto; Cilium como alternativa documentada (verificar compatibilidad con Istio).

## Consecuencias
Por determinar al decidir.
