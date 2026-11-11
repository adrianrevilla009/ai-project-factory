# docs

La documentación de la fábrica, para personas. Lo que necesitas saber para usarla, mantenerla y entender por qué está diseñada así.

## Por dónde empezar
| Si quieres… | Lee |
|---|---|
| Crear un proyecto o mantener la fábrica, paso a paso | [`onboarding.md`](onboarding.md) |
| Entender cómo encajan skills, agentes, comandos, hooks y gates | [`architecture/overview.md`](architecture/overview.md) |
| Ver las fases del proyecto y quién aprueba cada gate | [`operating-model/`](operating-model/README.md) |
| Buscar una norma concreta | [`skills-index.md`](skills-index.md) |
| Saber cómo escribir una skill nueva | [`skill-writing-brief.md`](skill-writing-brief.md) |

## Contenido
| Documento | Qué contiene |
|---|---|
| [`onboarding.md`](onboarding.md) | Guía de uso: crear un proyecto, qué esperar y qué no, y cómo añadir una skill, un ADR, un servidor MCP o un hook |
| [`FACTORY_BRIEF.md`](FACTORY_BRIEF.md) | El brief de partida: alcance original, decisiones D1–D27 y principios. Tiene una nota de vigencia al principio con lo que cambió después |
| [`skills-index.md`](skills-index.md) | **Generado** por `make index`: las skills por bloque con su descripción y nivel. No se edita a mano |
| [`skill-writing-brief.md`](skill-writing-brief.md) | Instrucciones para escribir una skill: estructura, límites de la descripción y cómo referenciar el enforcement |
| [`architecture/`](architecture/README.md) | Visión de conjunto, servidores MCP y formatos de Claude Code |
| [`operating-model/`](operating-model/README.md) | Ciclo de vida de un proyecto generado y matriz de responsabilidades de los gates |

## Cómo se mantienen
- Los documentos de esta carpeta están escritos en español y se revisan con cada cambio relevante de la fábrica.
- `make validate` comprueba que las cifras que citan (número de skills, agentes, comandos, hooks, ADR) coinciden con el repositorio y que sus enlaces no están rotos.
- Las decisiones de diseño no viven aquí sino en [`catalog/adr/`](../catalog/adr/README.md).
