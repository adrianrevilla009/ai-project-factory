---
name: domain-discovery
description: "Usar al arrancar un dominio nuevo o poco claro: sesiones de event storming para descubrir eventos, agregados, contextos delimitados y lenguaje ubicuo."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "reviewer"
---

# Descubrimiento de dominio (event storming)

## Cuándo aplicar y cuándo no
- Aplica al inicio de un proyecto, al abordar un subdominio nuevo o cuando el equipo no comparte vocabulario con negocio.
- No aplica a CRUD sin lógica de negocio relevante, ni a cambios pequeños en un modelo ya acordado.
- Con agentes: el agente `domain-analyst` propone y estructura; la validación del modelo la hace una persona experta de negocio.

## Reglas
- **MUST** descubrir primero los **eventos de dominio** en pasado (`PedidoPagado`, `ReembolsoSolicitado`) en una línea temporal, antes de hablar de tablas o servicios.
- **MUST** pasar por las tres fases: Big Picture (eventos y tensiones), Process Modeling (comandos, actores, políticas, read models) y Software Design (agregados y límites).
- **MUST** capturar **hotspots** (dudas, conflictos, reglas desconocidas) como preguntas abiertas con dueño, no resolverlos a mano alzada.
- **MUST** derivar candidatos a bounded context y agregados a partir de los clústeres de eventos y de cambios de lenguaje, no de la organización actual por defecto.
- **MUST** registrar el **lenguaje ubicuo** en un glosario versionado; un término = un significado por contexto.
- **SHOULD** invitar a negocio, desarrollo y operación; sin expertos de dominio, el resultado es una hipótesis.
- **SHOULD** convertir los resultados en artefactos del repo: glosario, mapa de contextos, eventos candidatos, ADR de los límites elegidos.
- **MUST NOT** tratar el resultado como diseño final: los límites se revisan con evidencia.
- **MUST NOT** introducir normativa como hecho: lo regulatorio detectado se anota "por confirmar con fuente oficial".

## Por qué
Los errores de límites son los más caros de corregir. Event storming (Alberto Brandolini) hace visible el conocimiento disperso con notas adhesivas por colores y obliga a conversar con negocio antes de diseñar. Los eventos son más estables que las estructuras de datos y orientan agregados, contextos e integración asíncrona.

## Ejemplos
### Mal
```text
Reunión de arquitectura: "tendremos servicios Order, Customer, Payment, Notification"
(derivados del esquema de base de datos existente, sin hablar con negocio)
```
### Bien
```yaml
# docs/domain/event-storming-2026-11.yaml (salida de la sesión)
events:
  - OrderPlaced
  - PaymentCaptured
  - RefundRequested
  - RefundApproved
hotspots:
  - id: HS-01
    question: "¿Quién aprueba reembolsos > 500 EUR?"
    owner: "product-owner"
    due: "2026-11-14"
bounded_contexts:
  - name: Billing
    aggregates: [Payment, Refund]
glossary:
  Refund: "Devolución parcial o total de un pago ya capturado (contexto Billing)."
```

## Checklist de revisión
- [ ] Línea temporal de eventos en pasado, validada con expertos.
- [ ] Hotspots listados con dueño y fecha.
- [ ] Candidatos a contextos/agregados justificados por eventos y lenguaje.
- [ ] Glosario versionado en el repo.
- [ ] Decisiones de límites recogidas en ADR.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión humana del modelo con expertos de negocio | 3 | gate de fase (ver `gate-protocol`); no automatizable |
| Revisión de coherencia de contextos y agregados | 3 | agentes `domain-analyst` y `architecture-guardian` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `ddd-strategic`, `ddd-tactical`, `aggregates-and-event-design`, `requirements-engineering`, `adr`.
- Fuentes: https://www.eventstorming.com/ (Brandolini).
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
