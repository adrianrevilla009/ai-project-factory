# Cómo encaja la fábrica

Una vista de conjunto: qué es cada pieza, cómo se conectan y por qué una regla escrita en una skill acaba siendo algo que se cumple de verdad.

## Dos capas
1. **La fábrica (este repo):** solo guías (ADR-0038). Skills, agentes, comandos, hooks, gates, catálogo, políticas de ejemplo y conocimiento. No genera código.
2. **Un proyecto generado:** vive en otra carpeta. Los agentes lo construyen siguiendo las guías y le copian lo que necesita para trabajar solo: hooks, agentes, comandos, skills activas y su `CLAUDE.md` (skill `bootstrap-generated-project-claude-config`).

## Piezas y para qué sirve cada una
| Pieza | Dónde | Papel |
|---|---|---|
| Skills | `.claude/skills/` | La norma: cuándo aplicar, reglas (MUST/SHOULD), por qué, ejemplos, checklist y cómo se hace cumplir. 490 en 31 bloques |
| Agentes | `.claude/agents/` | Roles con herramientas limitadas: negocio, entrega, ingeniería, calidad y gobierno |
| Comandos | `.claude/commands/` | El flujo por fases, de la entrevista inicial al cierre |
| Hooks | `.claude/hooks/` | Código determinista que bloquea lo inseguro o fuera de proceso. Es lo que no depende de que el modelo «se acuerde» |
| Gates | `gates/` | Seis puntos de aprobación humana con registro firmado |
| Catálogo | `catalog/` | Datos: librerías prohibidas, tiers, paridad AWS/local, ADR, servidores MCP |
| Políticas | `policies/` | Reglas ejecutables de ejemplo (Semgrep, Rego, Kyverno, ArchUnit, frontend) |
| Conocimiento | `knowledge/` | Patrones, antipatrones e índice de decisiones |
| Validadores | `factory/validators/` | Mantienen coherente la propia fábrica |

## Cómo viaja una regla
Una regla vale lo que vale su mecanismo de cumplimiento. Ejemplos reales del repo:

| Regla | Skill | Datos o política | Hook |
|---|---|---|---|
| Sin Lombok (ADR-0027) | `no-lombok` | `catalog/forbidden-libraries.yaml`, regla Semgrep `java-no-lombok`, Maven Enforcer | `forbidden_deps` |
| Sin concatenar SQL | `sql-injection-prevention` | regla Semgrep `sql-string-concatenation` | `format_and_lint` |
| Arquitectura hexagonal | `hexagonal`, `layering-rules-archunit` | reglas ArchUnit de ejemplo | `architecture_guard` |
| Probes y límites en Kubernetes | `workload-baseline` | política Kyverno `workload-baseline` | — |
| Aprobación humana | `gate-protocol` | `gates/approval-record.schema.json` | `enforce_gate_approval` |
| Honestidad sobre AWS | `honest-claims-policy`, `maturity-labels` | validador `honest_claims`, regla Rego de madurez | `maturity_label_check` |
| Sin secretos | `secrets-management` | — | `block_secrets`, `block_secrets_in_prompt` |

## Los cuatro niveles de enforcement
Cada skill declara cómo se hace cumplir cada regla, del más fuerte al más débil:
1. **Política** automática (Semgrep, Rego, Kyverno, ArchUnit, CI).
2. **Hook** del agente.
3. **Revisor**: un agente de solo lectura.
4. **Humano**: un gate.

Una fila «pendiente» significa que el mecanismo lo implementa el proyecto generado; la regla sigue siendo obligatoria y la revisan los niveles 3 y 4.

## Qué se comprueba de la propia fábrica
`make validate` verifica la estructura de las skills, que no haya afirmaciones deshonestas sobre AWS, los esquemas y ADR, el catálogo de MCP, que los enlaces de `knowledge/` existan y que los bloques de código sean sintácticamente válidos. `make test` prueba los hooks y los validadores.

## Para seguir
- Cómo usarla: [`onboarding.md`](../onboarding.md).
- Ciclo de vida y gates: [`project-lifecycle.md`](../operating-model/project-lifecycle.md) y [`RACI.md`](../operating-model/RACI.md).
- MCP: [`mcp.md`](mcp.md). Formatos de Claude Code: [`claude-code-formats.md`](claude-code-formats.md).
