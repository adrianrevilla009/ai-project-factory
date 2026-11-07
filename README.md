# AI Project Factory

Repositorio de **guías** para crear proyectos corporativos con IA: estándares (skills), agentes, comandos, hooks, policies, validadores y **gates humanos**. No contiene plantillas ni aplicación de referencia (ADR-0038): los agentes construyen el proyecto siguiendo las guías.

- Brief y decisiones: [`docs/FACTORY_BRIEF.md`](docs/FACTORY_BRIEF.md) · ADRs: [`catalog/adr/`](catalog/adr/README.md)
- Reglas permanentes: [`CLAUDE.md`](CLAUDE.md)

## Estado
| Pieza | Estado |
|---|---|
| Estructura, `CLAUDE.md`, gates 0–5, esquemas de dominio/normativa, `capabilities.yaml` | Creado |
| Skills: ver [`docs/skills-index.md`](docs/skills-index.md) (inventario en `catalog/skills-inventory.yaml`) | Redactados por bloques; contenido con muchos `TODO-VERIFY` pendientes de verificación en fuente oficial |
| 25 agentes (`.claude/agents/`) y 27 comandos (`.claude/commands/`) | Creado |
| Hooks (secretos, comandos peligrosos, gates, rutas, post-edición, stop, auditoría) | Creado y testeado |
| Policies (Semgrep, OPA/Conftest, Kyverno, ArchUnit, Enforcer) | Ejemplos iniciales **no ejecutados** (marcados `TODO-VERIFY`); muchas filas de enforcement figuran como "pendiente" |
| Validadores y generador de índice/estándares | Creado y testeado |
| Dev container con firewall | Creado, **no probado en un contenedor real** |

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
