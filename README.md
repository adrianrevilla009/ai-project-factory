# AI Project Factory

Repositorio de **guías** para que agentes de IA construyan proyectos corporativos con criterio de ingeniería de empresa: Java/Spring sobre Kubernetes, preparado para AWS, con puntos de control humanos. Aquí no hay plantillas, generadores ni aplicación de referencia (ADR-0038): hay normas, y mecanismos para que se cumplan.

Qué contiene:

| Pieza | Dónde | Cuántas |
|---|---|---|
| Skills (estándares con ejemplos, checklist y enforcement) | `.claude/skills/` | 490 en 31 bloques, ver [índice](docs/skills-index.md) |
| Agentes por rol | `.claude/agents/` | 28 |
| Comandos por fase del proyecto | `.claude/commands/` | 29 |
| Hooks que bloquean acciones inseguras o fuera de proceso | `.claude/hooks/` | 18, con tests |
| Gates de aprobación humana | `gates/` | 6 (0–5) |
| Decisiones de arquitectura | `catalog/adr/` | 38 |
| Reglas ejecutables de ejemplo | `policies/` | Semgrep, Rego, Kyverno, ArchUnit, ESLint |

El brief que define todo esto es [`docs/FACTORY_BRIEF.md`](docs/FACTORY_BRIEF.md); las reglas permanentes para los agentes, [`CLAUDE.md`](CLAUDE.md).

## Cómo se usa
Un agente, abierto en un proyecto nuevo, sigue el ciclo de [`docs/operating-model/project-lifecycle.md`](docs/operating-model/project-lifecycle.md): entrevista de intake → Gate 0 (dominio y normativa validados por personas) → plan → Gate 1 → implementación → Gate 2 → PR → Gate 3 → release → Gate 4 → revisión cloud → Gate 5 → cierre. En cada gate el agente prepara la evidencia y se detiene; una persona crea `approvals/gate-N.json` y el hook `enforce_gate_approval` impide avanzar sin él. La skill `bootstrap-generated-project-claude-config` define cómo el agente crea el `.claude/` del proyecto nuevo.

## Mantenimiento de este repo
```bash
make setup      # instala dependencias de desarrollo (Python 3)
make validate   # valida skills, claims sobre AWS, esquemas, ADRs e índice
make test       # tests de hooks y validadores
make check      # validate + test
make index      # regenera docs/skills-index.md y standards/ tras tocar una skill
```

## Honestidad sobre AWS
Nada de lo que produce esta fábrica se despliega en AWS (ADR-0004). La infraestructura que describa como mucho es *validada estáticamente*: **preparada para AWS, no verificada en real**, y puede fallar la primera vez que se aplique. `honest_claims.py` y el hook `maturity_label_check` rechazan afirmaciones en contrario.

## Estado
- **Estructura y mecanismos:** completos y con tests (`make check` en verde).
- **Contenido de las skills:** guías teóricas. Las versiones, flags y sintaxis de herramientas de terceros no se fijan aquí: se fijan en el BOM de cada proyecto y se contrastan con la documentación de la versión adoptada. Los datos concretos que sí aparecen (límites de AWS, licencias, nombres de propiedades, versiones de API) se verificaron contra fuentes oficiales y llevan su fecha. Lo que un agente no pueda comprobar en un proyecto, lo declara «no comprobado».
- **Políticas:** las 46 reglas de Semgrep están probadas (`make policy-test`); Rego, Kyverno, ArchUnit y frontend son ejemplos escritos sin ejecutar ([detalle](policies/README.md)).
- **Dev container y firewall:** sin probar en un contenedor real.
- **Texto legal y de cumplimiento:** borrador que debe confirmar una persona.
- **Decisiones y gates:** los ADR 0032–0037 y el RACI de gates están aceptados por el dueño (2026-11-09).
