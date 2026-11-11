---
name: rfc-process
description: "Usar cuando un cambio amplio o controvertido necesita debate escrito y consenso antes de decidir (impacto en varios equipos): proceso RFC previo al ADR."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-09"
  enforcement: "reviewer"
---

# Proceso RFC

## Cuándo aplicar y cuándo no
- Aplica a cambios transversales: nueva plataforma, ruptura de contrato público, cambio de modelo de datos compartido, nuevo estándar interno.
- No aplica a decisiones acotadas a un servicio (basta un ADR) ni a cambios reversibles baratos (basta un PR).
- Un RFC propone y debate; el ADR registra lo decidido. Un RFC aceptado termina en uno o más ADR.

## Reglas
- **MUST** escribir el RFC en un documento versionado (`docs/rfc/NNNN-titulo.md`) con: resumen, motivación, propuesta, alternativas, impacto, plan de migración/rollback, riesgos y preguntas abiertas.
- **MUST** indicar estado (`borrador`, `en revisión`, `aceptado`, `rechazado`, `retirado`), autor, revisores obligatorios y fecha límite de comentarios.
- **MUST** dar un plazo de revisión mínimo (p. ej. 5 días laborables) y avisar a todos los equipos afectados.
- **MUST** que los comentarios bloqueantes se resuelvan o se registren como objeción explícita con respuesta.
- **MUST** nombrar a quien decide (persona o comité); el consenso se busca, pero la decisión tiene dueño.
- **MUST** al aceptar, crear los ADR derivados y enlazar RFC y ADR entre sí.
- **SHOULD** prototipar o medir cuando haya hipótesis de rendimiento o coste, en lugar de opinar.
- **MUST NOT** implementar a gran escala antes de aceptar el RFC (spikes acotados sí).
- **MUST NOT** usar un RFC para saltarse una decisión cerrada D1-D27 sin ADR sustitutorio y aprobación humana.

## Por qué
Decidir en reuniones deja a los ausentes sin voz y no deja rastro. Un documento revisable asíncronamente captura objeciones temprano, cuando corregir es barato, y crea un registro. Limitar el proceso a cambios amplios evita burocracia en lo pequeño.

## Ejemplos
### Mal
```text
Mensaje en el chat: "Pasamos todos los servicios a gRPC la semana que viene, ¿ok?"
(sin documento, sin plazo, sin alternativas, sin dueño de la decisión)
```
### Bien
```markdown
# RFC-0007: Versionado de eventos con schema registry

- **Estado:** en revisión
- **Autor:** backend-java · **Decide:** solution-architect
- **Comentarios hasta:** 2026-11-14
- **Equipos afectados:** Billing, Orders, Data

## Motivación
Hoy los cambios de esquema rompen consumidores sin aviso.

## Propuesta
Registro de esquemas con compatibilidad BACKWARD (ver asyncapi-event-contracts).

## Alternativas
1. Versionar en el nombre del topic. 2. Sin registro, solo contract tests.

## Plan de migración y rollback
...

## Preguntas abiertas
- ¿Quién opera el registro en local? (OP-1, dueño: platform-engineer)
```

## Criterios de decisión y trampas
### Cómo decidir
- Una propuesta escrita para cambios que afectan a varios equipos, con un plazo de comentarios y un responsable de decidir.
- Para cambios locales, un ADR basta.
### Trampas frecuentes
- RFC para todo.
- Sin plazo ni decisor: la discusión no acaba.
- Propuestas sin alternativas.
- Decisiones tomadas fuera del documento.
- RFC que nadie lee.
### Evidencia
- Cada RFC tiene decisor, plazo y un resultado registrado.

## Checklist de revisión
- [ ] Secciones obligatorias completas, con alternativas y rollback.
- [ ] Decisor, revisores y fecha límite definidos.
- [ ] Equipos afectados notificados.
- [ ] Objeciones respondidas por escrito.
- [ ] Al aceptar, ADR creados y enlazados.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Revisión de cumplimiento de plantilla y de decisión cerrada | 3 | agentes `solution-architect` y `architecture-guardian` |
| Validador de estructura de RFC | - | pendiente |

> Estado: proceso sin automatización; la decisión final es humana.

## Relacionados, fuentes y mantenimiento
- Relacionados: `adr`, `library-selection-and-tech-radar-process`, `c4-and-arc42`, `change-and-release-management`.
- Fuentes: práctica extendida en la industria (p. ej. proceso RFC de proyectos open source); sin norma única.
- Nombres, flags, versiones y sintaxis de herramientas de terceros: se fijan en el BOM del proyecto y se contrastan con la documentación de la versión adoptada (`bom-management`).
- Dueño: factory-owner · Última revisión: 2026-11-09 · Nivel: T1
