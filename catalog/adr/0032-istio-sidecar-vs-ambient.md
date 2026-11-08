# ADR-0032: Istio: sidecar vs ambient

- **Estado:** aceptado (por defecto; revisable por el dueño)
- **Fecha:** 2026-11-07

## Contexto
Decisión abierta del brief (§3). No se inventa una respuesta; requiere confirmación humana.

## Opciones
- Sidecar: maduro, más recursos por pod.
- Ambient: menos sobrecarga; GA desde Istio 1.24 (ztunnel, waypoint y APIs estables); su multicluster multi-red es beta desde 1.29. Fuente: istio.io (anuncio de GA en 1.24 y feature stages).

## Decisión
Sidecar (por defecto, más maduro); ambient como alternativa documentada en el skill sidecar-vs-ambient-decision (ambient ya es GA; se mantiene sidecar por defecto por madurez operativa y menor riesgo en multicluster).

## Consecuencias
Por determinar al decidir.
