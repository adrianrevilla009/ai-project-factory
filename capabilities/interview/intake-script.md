# Guion de entrevista de intake (Gate 0)

Conduce `product-owner` (con `business-analyst`). Una pregunta cada vez; registra respuestas literales y marca como **supuesto** todo lo no confirmado.

## Bloque A · Negocio y alcance
1. ¿Qué problema resuelve el sistema y para quién? ¿Qué es éxito medible (KPIs)?
2. ¿Qué queda fuera de alcance de la primera versión?
3. ¿Quién decide y quién aprueba cada gate? (RACI en `docs/operating-model/RACI.md`)

## Bloque B · Capacidades (rellena `capabilities/capabilities.yaml`)
Para cada pregunta de `capabilities.yaml`: formula el `prompt`, anota la respuesta y la justificación. Si se responde "no sé", aplica el `default` y regístralo como supuesto.
- Si `full_history = true`: antes de aceptar event sourcing, pregunta si basta un audit trail inmutable (skill `audit-trail-without-event-sourcing`).
- `resilience_tier`: explica RPO/RTO de `catalog/resilience-tiers.yaml` y su coste relativo; defecto Tier 1.

## Bloque C · Datos y cumplimiento
1. ¿Qué datos personales o especiales se tratan? ¿Residencia de datos? → `compliance-framework/applicability-questionnaire.yaml`.
2. ¿Hay sectores regulados o auditorías previstas? Solo recoge; la matriz la prepara `compliance-analyst` como borrador por confirmar.

## Bloque D · Restricciones técnicas
Sistemas existentes, integraciones, equipos, hosting actual, límites de coste, recursos locales de desarrollo (perfil mínimo/completo).

## Salidas
`docs/capabilities.yaml`, registro de supuestos (`domain-framework/assumptions-register.schema.yaml`), lista de preguntas abiertas y entrada para `/project-discover`.
