# ADR-0033: CNI en EKS: VPC CNI vs Cilium

- **Estado:** aceptado (por defecto; revisable por el dueño)
- **Fecha:** 2026-11-07

## Contexto
Decisión abierta del brief (§3). No se inventa una respuesta; requiere confirmación humana.

## Opciones
- VPC CNI: nativo AWS.
- Cilium: más funciones; verificar compatibilidad con Istio.

## Decisión
VPC CNI por defecto; Cilium como alternativa documentada (verificar compatibilidad con Istio).

## Consecuencias
Por determinar al decidir.
