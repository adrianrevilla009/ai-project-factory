---
name: adr
description: "Usar al tomar, cambiar o revertir una decisión arquitectónica: cómo redactar, numerar, versionar y sustituir Architecture Decision Records en catalog/adr o docs/adr."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "policy"
---

# Architecture Decision Records (ADR)

## Cuándo aplicar y cuándo no
- Aplica a decisiones difíciles de revertir o que afectan a varios equipos/módulos: tecnología, estilo de integración, modelo de datos, seguridad, topología.
- No aplica a decisiones locales y reversibles (nombre de una clase); para propuestas amplias que necesitan debate previo, ver `rfc-process`.
- En la fábrica las decisiones D1-D27 ya tienen ADR cerrado en `catalog/adr/`; se cambian solo con un ADR nuevo que las sustituya.

## Reglas
- **MUST** escribir un ADR por decisión, numerado secuencialmente `NNNN-titulo-en-kebab.md`, y no reutilizar números.
- **MUST** incluir: `**Estado:**` (`propuesto`, `aceptado`, `rechazado`, `sustituido`), `**Fecha:**`, Contexto, Decisión, Por qué (opciones consideradas y descartadas) y Consecuencias (incluidas las negativas).
- **MUST** tratar los ADR aceptados como inmutables: para cambiar de criterio, crear un ADR nuevo y marcar el anterior `sustituido` con enlace cruzado.
- **MUST** enlazar el ADR desde el PR que lo implementa y desde la documentación afectada.
- **MUST** documentar al menos dos alternativas reales y por qué se descartaron.
- **SHOULD** incluir cómo se verificará la decisión (test de arquitectura, policy, métrica).
- **SHOULD** redactarlo en el mismo PR que el cambio o antes, nunca meses después.
- **MUST NOT** editar el cuerpo de un ADR aceptado para "corregir" la historia; solo estado y enlaces.
- **MUST NOT** contradecir una decisión cerrada D1-D27 sin ADR que la sustituya y aprobación humana.

## Por qué
El código muestra qué se hizo, no por qué. Sin ADR el equipo repite debates o deshace decisiones sin conocer el contexto. La plantilla MADR (adr.github.io/madr, consultada 2026-11-07) recoge contexto, opciones, resultado y consecuencias; esta fábrica usa una variante en español más corta, con el campo de estado exigido por el validador.

## Ejemplos
### Mal
```markdown
# Usamos Kafka
Decidido en la reunión del martes.
```
### Bien
```markdown
# ADR-0039: Mensajería de eventos entre Billing y Orders

- **Estado:** propuesto
- **Fecha:** 2026-11-07

## Contexto
Billing y Orders necesitan intercambiar eventos con entrega al menos una vez.

## Decisión
Kafka con outbox transaccional (ver ADR-0014).

## Por qué
Opciones: (A) Kafka + outbox, (B) llamadas REST síncronas, (C) cola gestionada.
B acopla disponibilidad; C añade dependencia no cubierta por la matriz local.

## Consecuencias
+ Desacople temporal. - Consumidores idempotentes obligatorios.
```

## Checklist de revisión
- [ ] Número nuevo, nombre en kebab-case, sin huecos ni duplicados.
- [ ] Estado válido y fecha presente.
- [ ] Al menos dos alternativas con motivo de descarte.
- [ ] Consecuencias negativas explícitas.
- [ ] Si sustituye a otro, ambos se enlazan y el antiguo pasa a `sustituido`.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Validador: cada decisión D1-D27 tiene ADR con `**Estado:**` válido | 1 | `factory/validators/schemas_and_adrs.py` |
| Revisión de calidad y de contradicciones con decisiones cerradas | 3 | agente `architecture-guardian` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `rfc-process`, `c4-and-arc42`, `library-selection-and-tech-radar-process`, `architecture-testing-archunit`.
- Fuentes: https://adr.github.io/madr/ (2026-11-07); Michael Nygard, "Documenting Architecture Decisions" (por nombre; URL y versión se fijan al adoptarlas en el proyecto).
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
