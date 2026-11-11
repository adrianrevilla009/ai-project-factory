# architecture

Documentos sobre cómo está construida la fábrica y sobre las piezas de Claude Code de las que depende.

| Documento | Qué explica |
|---|---|
| [`overview.md`](overview.md) | Las dos capas (la fábrica y los proyectos generados), el papel de cada pieza, cómo viaja una regla desde una skill hasta que se cumple y los cuatro niveles de enforcement |
| [`mcp.md`](mcp.md) | Cómo se gobiernan los servidores MCP: por qué la fábrica no ejecuta ninguno, qué incluye el catálogo, cómo funcionan los ámbitos, la aprobación y los permisos en Claude Code, y los criterios de selección |
| [`claude-code-formats.md`](claude-code-formats.md) | Los formatos de configuración de Claude Code que usa la fábrica (hooks, eventos, subagentes, skills, comandos, MCP y permisos), contrastados con la documentación oficial y con su fecha de verificación |

## Cuándo consultarlos
- Antes de tocar un hook, una skill, un agente o un comando: `claude-code-formats.md` dice qué admite la plataforma y qué no (por ejemplo, que las skills en subcarpetas no se descubren).
- Antes de proponer un servidor MCP: `mcp.md`.
- Para incorporarte al proyecto: `overview.md`.

Las decisiones que explican estos diseños están en [`catalog/adr/`](../../catalog/adr/README.md).
