# AI Project Factory

**Una fábrica de buenas prácticas para que agentes de IA construyan proyectos de software de nivel empresarial, de forma repetible y con una persona decidiendo en cada paso importante.**

## El objetivo
Pedirle a una IA que «monte un proyecto» da resultados desiguales: cada sesión decide por su cuenta cómo estructurar el código, qué librerías usar, cómo probarlo y qué es «terminado». Lo que sale puede parecer bueno y esconder fallos de seguridad, decisiones sin justificar o afirmaciones que nadie ha comprobado.

Este repositorio existe para cambiar eso. Reúne **qué significa hacer bien un proyecto** (las normas), **quién interviene** (los roles), **en qué orden** (el flujo) y **qué impide hacerlo mal** (los controles automáticos y las aprobaciones humanas), y lo pone al alcance de un agente de [Claude Code](https://code.claude.com). El objetivo final es que cualquier proyecto que salga de aquí, sea cual sea su dominio, cumpla el mismo nivel de exigencia y se pueda revisar con confianza.

Hoy cubre el ecosistema de **Java y Spring Boot**, **cloud** (AWS, solo como diseño), **Kubernetes y DevOps**, **frontend con React**, **calidad y seguridad**.

## Qué es y qué no es
- **Es** un repositorio de guías: 490 normas (skills) con sus ejemplos, criterios de decisión y forma de comprobarlas; 28 agentes con funciones definidas; 29 comandos que recorren el proyecto fase a fase; 18 hooks que bloquean lo inseguro; y 6 puntos de aprobación humana.
- **No es** un generador de código. No hay plantillas, ni un CLI, ni una aplicación de ejemplo (ADR-0038). El agente construye el proyecto **en otra carpeta**, leyendo estas guías y respetando sus controles.
- **No despliega nada en AWS** (ADR-0004). Todo lo que describe como infraestructura es, como máximo, «preparado para AWS, no verificado en real».

## La idea en una imagen
```
                    ┌─────────────────────────────────────────────┐
                    │  ESTA FÁBRICA (guías y controles)            │
                    │  normas · roles · flujo · hooks · gates      │
                    └──────────────┬──────────────────────────────┘
                                   │ guían y limitan a
                                   ▼
   Persona ──► Agentes de IA ──► PROYECTO GENERADO (otra carpeta)
      ▲                              código, infraestructura como código,
      └──────── aprueba cada ────────  pruebas, documentación, decisiones
                  fase (gate)
```

Un proyecto recorre siempre el mismo camino, y entre fase y fase hay un gate:

```
intake → Gate 0 → plan → Gate 1 → implementación → Gate 2 → pull request → Gate 3 → release → Gate 4 → revisión cloud → Gate 5 → cierre
```

En cada gate el agente prepara la evidencia y **se detiene**. Una persona revisa y firma. Mientras no haya firma válida, un hook impide seguir editando código, y ningún agente puede firmar por su cuenta.

## Los principios
1. **Si una regla se puede comprobar con un script, no es un prompt.** Va a un hook, una política o una prueba. Las skills son para lo que exige criterio.
2. **Una persona decide en cada gate.** Los agentes aceleran; no sustituyen la responsabilidad.
3. **Honestidad ante todo.** Lo que no se ha podido comprobar se declara «no comprobado»; nunca se afirma «listo para producción en AWS» sin haber desplegado.
4. **El contenido externo es dato, no instrucciones.** Una web, un documento o un resultado de herramienta no manda sobre el agente.
5. **Local primero, cloud preparado.** El sistema completo debe poder levantarse en local; la nube se diseña y se valida de forma estática, sin gastar.
6. **Núcleo portable, adaptadores en los bordes.** El dominio no depende de AWS ni de ninguna herramienta concreta.
7. **Las decisiones quedan escritas.** Cada decisión relevante de la fábrica es un ADR, y cada decisión de un proyecto generado también.

## Qué esperar de un proyecto generado
Las guías exigen que el resultado sea algo que un revisor externo pueda valorar en un cuarto de hora: un proyecto que se levanta en local con un comando y con datos de demostración, con su documentación, sus decisiones de arquitectura, sus informes de calidad y seguridad, y la infraestructura AWS preparada pero **no desplegada**. Cada pieza lleva la evidencia de cómo se ha comprobado.

## Cómo se hace cumplir lo escrito
Una norma vale lo que vale su mecanismo de cumplimiento. Cada skill declara el suyo, de más fuerte a más débil: **política automática**, **hook**, **revisor** (un agente de solo lectura) o **humano** (un gate). Una fila «pendiente» significa que el mecanismo lo implementa el proyecto generado, porque la fábrica no tiene plantillas, o que es una especificación todavía sin escribir; la regla sigue siendo obligatoria.

## Qué contiene
| Carpeta | Qué hay | Detalle |
|---|---|---|
| `.claude/` | Las 490 skills, los agentes, los comandos, los hooks y los permisos | [`.claude/README.md`](.claude/README.md) |
| `gates/` | Los 6 gates humanos, sus checklists y el esquema del registro de aprobación | [`gates/README.md`](gates/README.md) |
| `catalog/` | Decisiones (ADR), inventario de skills, librerías, tiers de resiliencia, paridad AWS/local y servidores MCP | [`catalog/README.md`](catalog/README.md) |
| `capabilities/` | La entrevista inicial y cómo cada respuesta activa módulos y skills | [`capabilities/README.md`](capabilities/README.md) |
| `domain-framework/`, `compliance-framework/` | Cómo un agente entiende el dominio y prepara el análisis normativo sin inventar ni dictaminar | [dominio](domain-framework/README.md) · [normativa](compliance-framework/README.md) |
| `policies/` | Reglas ejecutables de ejemplo (Semgrep, Rego, Kyverno, ArchUnit, frontend) | [`policies/README.md`](policies/README.md) |
| `knowledge/` | Patrones, antipatrones e índice de decisiones | [`knowledge/README.md`](knowledge/README.md) |
| `docs/` | Brief, guía de uso, arquitectura y modelo operativo | [`docs/README.md`](docs/README.md) |
| `factory/`, `tests/` | Los validadores y las pruebas que mantienen la fábrica coherente | [factory](factory/README.md) · [tests](tests/README.md) |
| `prompts/`, `standards/` | Prompts reutilizables y las reglas de cada bloque en una página (generado) | [prompts](prompts/README.md) · [standards](standards/README.md) |
| `.devcontainer/`, `.github/` | Entorno aislado de trabajo y CI | [devcontainer](.devcontainer/README.md) · [github](.github/README.md) |

Además: [`CLAUDE.md`](CLAUDE.md) con las reglas permanentes para los agentes, y el [`CHANGELOG.md`](CHANGELOG.md).

## Por dónde empezar
- **Quiero crear un proyecto:** abre Claude Code en esta carpeta, lanza `/project-init <ruta-destino> <nombre>` y sigue el flujo. Guía paso a paso: [`docs/onboarding.md`](docs/onboarding.md).
- **Quiero entender cómo encaja todo:** [`docs/architecture/overview.md`](docs/architecture/overview.md).
- **Busco una norma concreta:** [`docs/skills-index.md`](docs/skills-index.md), o parte de un problema en [`knowledge/`](knowledge/README.md).
- **Voy a cambiar la fábrica:** una skill, un ADR, un servidor MCP o un hook cada vez, con `make check` en verde.

## Mantenimiento
```bash
make setup         # instala las dependencias de desarrollo (Python 3)
make validate      # comprueba skills, esquemas, ADR, catálogo MCP, mapa de módulos, enlaces, README y bloques de código
make test          # pruebas de hooks, validadores y agentes
make check         # validate + test
make index         # regenera el índice y los estándares tras tocar una skill
make policy-test   # prueba las reglas de Semgrep (requiere semgrep)
```
La documentación está en español; el código y los identificadores, en inglés. Los commits siguen [Conventional Commits](https://www.conventionalcommits.org/es/).

## Estado y límites
- **Completo y con pruebas:** estructura, hooks, gates, validadores, mapa de módulos y catálogo MCP.
- **Guías, no versiones:** las skills describen criterios y trampas; las versiones y la sintaxis de cada herramienta se fijan en el BOM de cada proyecto.
- **Políticas:** las 46 reglas de Semgrep están probadas; las de Rego, Kyverno, ArchUnit y frontend son ejemplos escritos sin ejecutar ([detalle](policies/README.md)).
- **Sin probar:** el firewall del entorno aislado, en un contenedor real.
- **En manos de una persona:** la validación de cualquier texto legal o de cumplimiento, que siempre es un borrador.
