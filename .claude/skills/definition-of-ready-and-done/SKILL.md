---
name: definition-of-ready-and-done
description: "Usar al planificar o cerrar una historia/tarea: criterios para empezar (Definition of Ready) y para darla por terminada (Definition of Done) con evidencia."
metadata:
  block: "30-engineering-process"
  tier: T1
  owner: "factory-owner"
  last_reviewed: "2026-11-07"
  enforcement: "hook"
---

# Definition of Ready y Definition of Done

## Cuándo aplicar y cuándo no
- Aplica a cada historia, bug o tarea técnica que entra en planificación (DoR) y a cada una que se declara terminada (DoD).
- No aplica a spikes de investigación con límite de tiempo: su salida es conocimiento (nota o ADR), no software desplegable.

## Reglas
### Definition of Ready (para empezar)
- **MUST** tener valor/objetivo claro y criterios de aceptación verificables (ver `requirements-engineering`).
- **MUST** tener requisitos no funcionales relevantes explícitos (latencia, seguridad, datos personales).
- **MUST** estar dimensionada para caber en una iteración corta; si no, dividirla.
- **MUST** tener dependencias identificadas (otros equipos, contratos, datos) y sin bloqueo abierto.
- **SHOULD** tener un enfoque técnico acordado; si implica decisión de arquitectura, existe ADR en `proposed`.
### Definition of Done (para cerrar)
- **MUST** cumplir todos los criterios de aceptación con tests automáticos que los demuestren.
- **MUST** pasar el pipeline completo: build, tests, lint, SAST, dependencias, cobertura según `coverage-policy`.
- **MUST** estar revisada y aprobada por PR (ver `pr-rules`).
- **MUST** tener docs actualizadas (README vivo, API docs, runbook si cambia la operación, ADR si hubo decisión) y entrada de changelog.
- **MUST** tener observabilidad mínima: logs estructurados, métricas y alertas afectadas revisadas.
- **MUST NOT** declarar "hecho" con deuda oculta: lo que se difiere se registra en el `tech-debt-register`.
- **MUST NOT** afirmar madurez de nube superior a "preparado para AWS, no verificado en real" (ADR-0004).

## Por qué
Sin DoR se empieza trabajo ambiguo y se descubre tarde que falta información; sin DoD "terminado" significa cosas distintas para cada persona y la deuda se acumula en silencio. Hacer ambos listas explícitas y comprobables vuelve la conversación objetiva.

## Ejemplos
### Mal
```markdown
Historia: "Mejorar el listado de pedidos"
Hecho cuando: "funciona en mi máquina"
```
### Bien
```markdown
Historia PAY-123: Como agente de soporte quiero reembolsar parcialmente un pedido...
DoR: [x] criterios Gherkin  [x] NFR: p95 < 300 ms  [x] contrato con Billing acordado
DoD: [x] tests verdes  [x] PR aprobado  [x] OpenAPI actualizado  [x] runbook revisado
     [x] CHANGELOG  [x] deuda diferida registrada (TD-014)
```

## Checklist de revisión
- [ ] La historia cumple DoR antes de entrar en la iteración.
- [ ] Cada criterio de aceptación tiene un test que lo ejecuta.
- [ ] Docs, changelog y ADR al día.
- [ ] Deuda diferida registrada, no escondida.
- [ ] Ninguna afirmación de madurez AWS por encima de lo verificable.

## Enforcement
| Mecanismo | Nivel | Dónde |
|---|---|---|
| Hook de parada: tests en verde | 2 | `.claude/hooks/stop/require_green_tests.py` |
| Hook de parada: docs actualizadas si hay código cambiado | 2 | `.claude/hooks/stop/require_docs_updated.py` |
| Validador de afirmaciones honestas | 1 | `factory/validators/honest_claims.py` |
| Verificación de DoR/DoD por agente | 3 | agentes `product-owner` y `qa-engineer` |

## Relacionados, fuentes y mantenimiento
- Relacionados: `requirements-engineering`, `pr-rules`, `quality-gates`, `coverage-policy`, `tech-debt-register`, `living-readme`.
- Fuentes: The Scrum Guide define "Definition of Done" (scrumguides.org, comprobar redacción actual); DoR es práctica común, no parte del Scrum Guide.
- Dueño: factory-owner · Última revisión: 2026-11-07 · Nivel: T1
