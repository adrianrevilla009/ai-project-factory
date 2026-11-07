# ADR-0032: Istio: sidecar vs ambient

- **Estado:** aceptado (por defecto; revisable por el dueño)
- **Fecha:** 2026-11-07

## Contexto
Decisión abierta del brief (§3). No se inventa una respuesta; requiere confirmación humana.

## Opciones
- Sidecar: maduro, más recursos por pod.
- Ambient: menos sobrecarga, TODO-VERIFY madurez y compatibilidad con la versión elegida.

## Decisión
Sidecar (por defecto, más maduro); ambient como alternativa documentada en el skill sidecar-vs-ambient-decision (TODO-VERIFY madurez vigente).

## Consecuencias
Por determinar al decidir.
