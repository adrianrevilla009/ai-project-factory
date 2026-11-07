# AI Project Factory

Repositorio de **guías** para crear proyectos corporativos con IA: estándares (skills), agentes, comandos, hooks, policies, validadores y **gates humanos**. No contiene plantillas ni aplicación de referencia (ADR-0038): los agentes construyen el proyecto siguiendo las guías.

- Brief y decisiones: [`docs/FACTORY_BRIEF.md`](docs/FACTORY_BRIEF.md) · ADRs: [`catalog/adr/`](catalog/adr/README.md)
- Reglas permanentes: [`CLAUDE.md`](CLAUDE.md)

## Estado: Oleada 0 (fundaciones)
| Pieza | Estado |
|---|---|
| Estructura de carpetas, gates, esquemas de dominio/normativa | Creado |
| Skills: plantilla + 4 de agentic-engineering + `n-plus-one` (ejemplo completo) | Creado |
| ADRs D1–D27 + decisiones abiertas (propuestas) | Creado |
| Hooks `block-secrets`, `block-dangerous-commands`, `enforce-gate-approval` | Creado y testeado |
| Validadores (skills, afirmaciones honestas, esquemas, ADRs) | Creado y testeado |
| Dev container con firewall de salida | Creado, **no probado en un contenedor real** |
| Resto de skills, agentes, comandos, policies | Pendiente (Oleadas 1–5) |

## Uso
```bash
make setup      # dependencias Python
make validate   # validadores
make test       # tests de hooks y validadores
make check      # ambos
```

## Honestidad sobre AWS
Esta fábrica **nunca despliega en AWS** (ADR-0004). La infraestructura AWS que genere es como máximo *validada estáticamente*: **preparado para AWS, no verificado en real**. El código puede fallar la primera vez que se aplique (permisos, límites de cuenta, orden de dependencias). El validador rechaza afirmaciones en contrario.

## Capas
1. **Fábrica** (este repo): estándares, skills, agentes, hooks, plantillas, validadores.
2. **Proyectos generados**: el producto + su propio `.claude/` y `CLAUDE.md`.

## Flujo
Gate 0 Intake → 1 Plan → 2 Implementación → 3 PR → 4 Release → 5 Cloud readiness → cierre. Cada gate exige un registro de aprobación humano ([`gates/`](gates/)); el hook `enforce-gate-approval` lo hace cumplir.

## Hoja de ruta
Oleada 1 núcleo Java/calidad (guías, policies, hooks) · 2 arquitectura/observabilidad · 3 plataforma/entrega · 4 persistencia políglota/frontend · 5 módulos T2.
