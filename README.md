# AI Project Factory

Repositorio de **guías** para que agentes de IA construyan proyectos corporativos de cualquier tamaño con criterio de ingeniería de empresa. Cubre Java y Spring Boot, cloud (AWS solo como diseño), Kubernetes, DevOps, frontend con React, calidad y seguridad. Todo está pensado para que lo consuma [Claude Code](https://code.claude.com), con puntos de control humanos en cada fase.

## Qué es
Una colección de normas escritas para agentes y de los mecanismos que las hacen cumplir:

- **Skills:** una norma por tema, con reglas, ejemplos, checklist y la forma exacta de comprobarla. 490, agrupadas en 31 bloques.
- **Agentes y comandos:** los roles (negocio, entrega, ingeniería, calidad, gobierno) y el flujo de trabajo por fases.
- **Hooks:** código determinista que bloquea lo inseguro o lo que se salta el proceso, sin depender de que el modelo «se acuerde».
- **Gates:** seis aprobaciones humanas que ningún agente puede dar por sí mismo.
- **Catálogo, políticas y conocimiento:** datos de referencia, reglas ejecutables de ejemplo, patrones y antipatrones.

## Qué no es
No contiene plantillas, generadores de código, una aplicación de ejemplo ni un CLI (ADR-0038). Los agentes construyen el proyecto en **otra carpeta** siguiendo estas guías. Tampoco despliega nada en AWS (ADR-0004): lo que escribe como infraestructura es, como máximo, «validado estáticamente».

## Mapa del repositorio
| Carpeta | Qué hay | Más información |
|---|---|---|
| `.claude/` | Skills, agentes, comandos, hooks y permisos que usan los agentes | [`.claude/README.md`](.claude/README.md) |
| `gates/` | Los 6 puntos de aprobación humana, sus checklists y el esquema del registro | [`gates/README.md`](gates/README.md) |
| `catalog/` | Datos: ADR, inventario de skills, librerías, tiers de resiliencia, paridad AWS/local, servidores MCP | [`catalog/README.md`](catalog/README.md) |
| `capabilities/` | Entrevista de intake y su mapa hacia módulos, skills y políticas | [`capabilities/README.md`](capabilities/README.md) |
| `domain-framework/` | Cómo un agente descubre el dominio sin inventarlo | [`domain-framework/README.md`](domain-framework/README.md) |
| `compliance-framework/` | Cómo un agente prepara el análisis normativo sin dictaminar | [`compliance-framework/README.md`](compliance-framework/README.md) |
| `policies/` | Reglas ejecutables de ejemplo: Semgrep, Rego, Kyverno, ArchUnit, frontend | [`policies/README.md`](policies/README.md) |
| `knowledge/` | Patrones, antipatrones e índice de decisiones | [`knowledge/README.md`](knowledge/README.md) |
| `prompts/` | Prompts reutilizables por los agentes | [`prompts/README.md`](prompts/README.md) |
| `standards/` | Las reglas de cada bloque de skills en una sola página (generado) | [`standards/README.md`](standards/README.md) |
| `docs/` | Brief, onboarding, arquitectura, modelo operativo e índice de skills | [`docs/README.md`](docs/README.md) |
| `factory/` | Los validadores y el generador del índice | [`factory/README.md`](factory/README.md) |
| `tests/` | Pruebas de hooks, validadores, reglas Semgrep y agentes | [`tests/README.md`](tests/README.md) |
| `.devcontainer/` | Entorno aislado de trabajo con firewall de salida | [`.devcontainer/README.md`](.devcontainer/README.md) |
| `.github/` | CI, responsables del código y plantilla de PR | [`.github/README.md`](.github/README.md) |

Además: [`CLAUDE.md`](CLAUDE.md) (reglas permanentes para los agentes), [`CHANGELOG.md`](CHANGELOG.md) y `VERSION`.

## Cómo funciona
Un proyecto generado recorre siempre el mismo ciclo, y entre fase y fase hay un gate:

```
intake → Gate 0 → plan → Gate 1 → implementación → Gate 2 → pull request → Gate 3 → release → Gate 4 → revisión cloud → Gate 5 → cierre
```

En cada gate el agente prepara la evidencia contra el checklist y **se detiene**. Una persona revisa y crea `approvals/gate-N.json`; el hook `enforce_gate_approval` impide editar código si falta un registro válido, y ningún agente puede escribir en `approvals/`. El detalle está en [`docs/operating-model/project-lifecycle.md`](docs/operating-model/project-lifecycle.md) y las responsabilidades de cada gate, en [`docs/operating-model/RACI.md`](docs/operating-model/RACI.md).

## Cómo se usa
- **Crear un proyecto:** abre Claude Code en esta carpeta, lanza `/project-init <ruta-destino> <nombre>` y sigue las fases. Paso a paso en [`docs/onboarding.md`](docs/onboarding.md).
- **Entender cómo encaja todo:** [`docs/architecture/overview.md`](docs/architecture/overview.md).
- **Buscar una norma:** [`docs/skills-index.md`](docs/skills-index.md) lista las skills por bloque, y [`knowledge/`](knowledge/README.md) te lleva a ellas desde un problema.
- **Cambiar la fábrica:** una skill, un ADR, un servidor MCP o un hook cada vez, con `make check` en verde. Cómo, en [`docs/onboarding.md`](docs/onboarding.md).

## Cómo se garantiza que lo escrito se cumple
Cada regla declara su mecanismo, de más fuerte a más débil:

1. **Política automática** (Semgrep, Rego, Kyverno, ArchUnit, CI).
2. **Hook** del agente.
3. **Revisor**: un agente de solo lectura.
4. **Humano**: un gate.

Una fila «pendiente» en la tabla de Enforcement de una skill significa que el mecanismo lo implementa el proyecto generado (la fábrica no tiene plantillas), o que es una especificación de la fábrica todavía sin escribir. La regla sigue siendo obligatoria y la comprueban los niveles 3 y 4.

## Mantenimiento
```bash
make setup         # instala las dependencias de desarrollo (Python 3)
make validate      # valida skills, afirmaciones sobre AWS, esquemas, ADR, catálogo MCP, mapa de módulos, enlaces, README y bloques de código
make test          # pruebas de hooks, validadores, agentes y evaluaciones de agentes
make check         # validate + test
make index         # regenera docs/skills-index.md y standards/ tras tocar una skill
make policy-test   # prueba las reglas de Semgrep (requiere semgrep instalado)
```

## Convenciones
- **Idioma:** la documentación y las skills, en español; el código, los identificadores y los comentarios de código, en inglés.
- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/es/) pequeños.
- **Honestidad sobre AWS:** la fórmula es «preparado para AWS, no verificado en real». `honest_claims.py` y el hook `maturity_label_check` rechazan afirmaciones en contrario.
- **Datos concretos:** versiones, flags y sintaxis de herramientas de terceros no se fijan aquí; se fijan en el BOM de cada proyecto. Lo que un agente no puede comprobar, lo declara «no comprobado».
- **Normativa:** todo texto legal o de cumplimiento es un borrador que valida una persona.

## Estado
- **Completo y con pruebas:** estructura, hooks, gates, validadores, mapa de módulos y catálogo MCP (`make check` en verde).
- **Guías teóricas:** las skills describen criterios y trampas, no fijan versiones de herramientas.
- **Políticas:** las reglas de Semgrep están probadas; Rego, Kyverno, ArchUnit y frontend son ejemplos sin ejecutar ([detalle](policies/README.md)).
- **Sin probar:** el firewall del dev container en un contenedor real.
- **Pendiente de una persona:** la validación de los textos legales y de cumplimiento.
- **Decisiones:** los ADR 0032–0037 y el RACI de gates están aceptados por el dueño (2026-11-09).
