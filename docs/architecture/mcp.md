# MCP en la fábrica y en los proyectos generados

La fábrica **no ejecuta ningún servidor MCP**: su `.mcp.json` está vacío a propósito. Lo que aporta es el criterio para elegir servidores y un catálogo ya revisado, que el agente `bootstrap-generated-project-claude-config` usa para escribir el `.mcp.json` de cada proyecto.

## Qué hay
| Pieza | Para qué |
|---|---|
| [`catalog/mcp-servers.yaml`](../../catalog/mcp-servers.yaml) | 11 servidores candidatos con propósito, transporte, origen, acceso (solo lectura o escritura), credenciales, roles y skills relacionadas. Lo valida `make validate`. |
| Skill `mcp-governance` | Reglas para añadir, aprobar y revisar servidores. |
| Skill `mcp-servers-in-java` | Cómo construir un servidor MCP propio en Java. |
| Skill `prompt-injection-defense-for-agents` | Por qué toda salida de un MCP es dato no confiable. |

## Cómo funciona en Claude Code (verificado el 2026-11-09 en code.claude.com/docs/en/mcp)
- **Ámbitos:** un servidor puede definirse para el usuario, el proyecto (`.mcp.json`, versionado) o localmente. Los de proyecto **piden aprobación** al abrir la carpeta y no se conectan en una carpeta no confiable aunque `settings.json` los habilite.
- **Variables de entorno:** `.mcp.json` admite `${VAR}`, de modo que el fichero se comparte sin secretos.
- **Permisos:** las reglas usan `mcp__<servidor>__<herramienta>`; un subagente restringe qué usa con su campo `tools` y puede declarar sus propios `mcpServers`.
- **Plugins:** un servidor empaquetado en un plugin se registra con nombre con ámbito (`plugin:<plugin>:<servidor>`); un hook escrito contra el nombre simple no se dispara.
- **Nombres reservados:** `workspace`, `claude-in-chrome`, `computer-use`, entre otros; no se pueden reutilizar.
- **Control central:** en configuración gestionada se pueden fijar listas `allowedMcpServers` y `deniedMcpServers`.

## Criterio de selección (resumen)
1. **Solo lectura por defecto.** Un servidor que escribe necesita un rol concreto y una regla de permisos que pida confirmación.
2. **Local antes que remoto.** Un servidor remoto o que consulta un servicio externo envía contenido a un tercero: queda marcado `data_leaves_machine: true` y exige no pegar código propietario.
3. **Nada que toque una cuenta AWS real** (ADR-0004). Los servidores de AWS del catálogo son de documentación y de diagramas.
4. **Versión exacta en el BOM del proyecto.** Nunca `latest`: un `npx` o `uvx` sin versión ejecuta código nuevo en cada arranque (cadena de suministro).
5. **Credenciales solo por `${VAR}`** y con el alcance mínimo y caducidad corta.
6. **Mínimos por proyecto.** Los servidores `default: true` del catálogo son tres (documentación de librerías, documentación de AWS y análisis estático); los demás se añaden cuando la entrevista o el rol lo justifican.

## Por qué no hay servidores propios de la fábrica
El brief original incluía `component-catalog`, `standards-lookup` y `lessons-search`. Se retiraron con el resto del código (ADR-0038). El mismo servicio lo cubre leer los ficheros de `catalog/`, `docs/skills-index.md` y `standards/`, que son texto.
